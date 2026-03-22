## Scaling Parameters

- Scaling cooldown: 360s _waiting period after a scaling activity (like adding or removing servers) during which no new scaling actions are triggered_
- Scaling metric: `TargetResponseTime` _time from when the load balancer forwards the request to a target until the target starts sending the response back_
- Breach duration: 2m _the amount of time a metric can exceed a threshold before triggering a scaling operation_
- Upper/Lower threshold: [150ms, 400ms]

If an alarm is hit for more then `BreachDuration` then a scaling activity is triggered, after that for `ScalingCooldown` amount of time no scaling activity can be triggered. 


