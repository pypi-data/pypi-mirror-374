"""
Health and Status logic
"""

from collections import defaultdict, deque
from dataclasses import dataclass
from threading import Event, Thread
import traceback
import time
import statistics
from typing import Callable, Literal
import avesterra as av
from orchestra import mount
from . import sysmon


class Health:
    status: Literal["GREEN", "YELLOW", "RED"]
    justification: str | None
    """If status is not GREEN, this field should contain a justification for the status"""

    @classmethod
    def _init(
        cls, status: Literal["GREEN", "YELLOW", "RED"], justification: str | None = None
    ):
        res = cls()
        res.status = status
        res.justification = justification
        return res

    @classmethod
    def green(cls):
        return cls._init("GREEN", None)

    @classmethod
    def yellow(cls, justification: str):
        return cls._init("YELLOW", justification)

    @classmethod
    def red(cls, justification: str):
        return cls._init("RED", justification)


@dataclass
class CallStat:
    restime: float
    """Response time of the call in seconds"""
    timestamp: float
    """Timestamp at which the call was made"""
    exception: Exception | None
    """The exception raised during the call, if any. If None, the call was successful."""


class MonitorStats:
    def __init__(self, hns: "Hns", name: str):
        self.hns = hns
        self.name = name
        self.start_time = None
        self._timemon_thread = None
        self._exitev = Event()
        self._did_timeout = False

    def __enter__(self):
        timeout = self._get_timeout([s.restime for s in self.hns.routes[self.name]])
        if timeout is not None:
            self._timemon_thread = Thread(
                target=self._monitor_restime,
                args=(timeout,),
                name=f"TimeoutMonitor-{self.name}",
                daemon=True,
            )
            self._timemon_thread.start()

        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        del traceback
        end_time = time.time()
        self._exitev.set()
        assert self.start_time is not None

        self.hns.routes[self.name].append(
            CallStat(
                restime=end_time - self.start_time,
                timestamp=self.start_time,
                exception=exc_value if exc_type else None,
            )
        )
        if not self._did_timeout:
            self.hns.recent_perf_good.append(True)

    def _monitor_restime(self, timeout: float):
        """Returns true if the timeout was reached, false otherwise."""
        ok = self._exitev.wait(timeout)
        if ok:
            return
        self._did_timeout = True
        av.av_log.warn(
            f"Performance issue detected for route {self.name}: "
            f"Still havn't finished after {timeout:.3f} seconds, which is statistically abnormal. Reporting it to sysmon."
        )
        self.hns.recent_perf_good.append(False)
        self.hns._refresh_hns()

    @staticmethod
    def _get_timeout(historical: list[float]) -> float | None:
        """
        If the route takes more time to respond than the threshold, it is considered a performance issue.
        The threshold is computed using the Interquartile Range (IQR) method.
        If the historical data is not enough to compute the threshold, None is returned.

        see https://en.wikipedia.org/wiki/Interquartile_range
        """
        # 1.5 is a common value for K in IQR method.
        K = 1.5
        MIN = 5

        if len(historical) < 50:
            # Not enough data to reliably compute the IQR threshold
            return None
        sorted_times = sorted(historical)
        q1 = sorted_times[int(len(sorted_times) * 0.25)]
        q3 = sorted_times[int(len(sorted_times) * 0.75)]
        iqr = q3 - q1
        threshold = q3 + K * iqr
        threshold = max(threshold, MIN)
        return threshold


class Hns:
    def __init__(
        self,
        component: av.AvEntity,
        authorization: av.AvAuthorization,
        statusfn: Callable[[], Health],
    ):
        self.component = component
        self.authorization = authorization
        self.statusfn = _statusfn_safety_wrapper(statusfn)
        self.routes: dict[str, deque[CallStat]] = defaultdict(
            lambda: deque[CallStat](maxlen=100)
        )
        self.recent_perf_good = deque[bool](maxlen=10)

        try:
            _check_sysmon_version(authorization)
        except Exception:
            av.av_log.error(
                f"/!\\ bug in orchestra-toolkit library: Uncaught exception while checking sysmon version. This error is probably harmless.\n{traceback.format_exc()}."
            )

    def run(self):
        while True:
            try:
                self._refresh_hns()
                time.sleep(25)  # not scientific
            except Exception:
                av.av_log.error(
                    f"/!\\ bug in orchestra-toolkit library: Uncaught exception while reporting health status. Status may not have been reported to sysmon: {traceback.format_exc()}"
                )

    def monitor(self, name: str) -> MonitorStats:
        return MonitorStats(self, name)

    def _refresh_hns(self):
        health = self.statusfn()

        try:
            sysmon.refresh_status(
                component=self.component,
                status=health.status,
                justification=health.justification,
                perfStatus="GREEN" if all(self.recent_perf_good) else "RED",
                authorization=self.authorization,
            )
        except Exception as e:
            av.av_log.warn(f"Invoke to sysmon failed: {e}")

        model = av.AvialModel()
        for name, metrics in self.routes.items():
            if not metrics:
                continue

            metrics = metrics.copy()  # in case the deque is modified during the loop
            restime_ordered = sorted(s.restime for s in metrics)
            avg_response_time = sum(restime_ordered) / len(restime_ordered)
            timespan = time.time() - metrics[0].timestamp

            d = {
                "sample size": av.AvValue.encode_integer(len(metrics)),
                "avg response time": av.AvValue.encode_float(
                    round(avg_response_time, 4)
                ),
                "avg call per minute": av.AvValue.encode_float(
                    round(len(metrics) / (timespan / 60.0), 1)
                ),
                "success rate %": av.AvValue.encode_float(
                    round(sum(100 for s in metrics if s.exception) / len(metrics), 1)
                ),
            }
            if len(metrics) > 1:

                d |= {
                    "response time stddev": av.AvValue.encode_float(
                        round(statistics.stdev(restime_ordered), 4)
                    ),
                    "response time p01": av.AvValue.encode_float(
                        round(restime_ordered[int(len(metrics) * 0.01)], 4)
                    ),
                    "response time p10": av.AvValue.encode_float(
                        round(restime_ordered[int(len(metrics) * 0.1)], 4)
                    ),
                    "response time p50": av.AvValue.encode_float(
                        round(restime_ordered[len(metrics) // 2], 4)
                    ),
                    "response time p90": av.AvValue.encode_float(
                        round(restime_ordered[int(len(metrics) * 0.9)], 4)
                    ),
                    "response time p99": av.AvValue.encode_float(
                        round(restime_ordered[int(len(metrics) * 0.99)], 4)
                    ),
                }
            model.attributions[av.AvAttribute.PERFORMANCE].traits[name].value = (
                av.AvValue.encode_aggregate(d)
            )

        try:
            av.store_entity(
                self.component,
                value=model.to_interchange(),
                authorization=self.authorization,
            )
            av.publish_event(
                self.component,
                event=av.AvEvent.UPDATE,
                attribute=av.AvAttribute.HEALTH,
                authorization=self.authorization,
            )
        except Exception as e:
            av.av_log.warn(f"Failed to store health and status in outlet: {e}")


def _statusfn_safety_wrapper(statusfn: Callable[[], Health]) -> Callable[[], Health]:
    def wrapped() -> Health:
        try:
            health = statusfn()
            if not isinstance(health, Health):
                av.av_log.error(
                    f"Health status function returned an invalid type: {type(health)}"
                )
                health = Health.red(
                    f"Health status function did not return a valid HealthReport object: {health}",
                )
        except Exception as e:
            av.av_log.error(
                f"Exception raised in the health status function: {e}, default to RED"
            )
            health = Health.red(f"Exception raised: {repr(e)}")
        return health

    return wrapped


def _check_sysmon_version(authorization: av.AvAuthorization):
    try:
        outlet = mount.get_outlet(sysmon.MOUNT_KEY, authorization)
    except Exception:
        return
    version = av.get_fact(outlet, av.AvAttribute.VERSION, authorization=authorization)
    versionstr = version.decode_string()
    # Not doing full semver parsing to not depend on third party
    major, minor, _ = map(int, versionstr.split("."))
    if major == 0 and minor < 3:
        raise RuntimeError(
            f"Sysmon outlet version {versionstr} is too old, please update the sysmon adapter to at least 0.3.0"
        )
