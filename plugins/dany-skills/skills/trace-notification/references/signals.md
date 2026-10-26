# Signal map

**Fill this in for your stack.** Every `<placeholder>` is a value from your own services: hosts,
paths, credentials, Prometheus jobs and labels, Loki labels, metric names, database names. The names
that are not in angle brackets (`message_dropped_total`, `NotificationService.list` and so on) are an
example from one notification service, kept so the reasoning is easy to follow. Swap them for yours.
Write the date you read it out of a live investigation, and re-check a name before trusting it.

Read on `<date>`.

## Reaching the service on dev

Base path is `<https://dev.example.com/api/notify>`, which maps to the service's own `/`.
So `@RequestMapping("/accounts")` is reachable at `<base path>/accounts`.

Auth is `<a shared Basic credential>` whose username is the calling service, **not a user**. Decoding it
tells you nothing about who should have received anything. Take the value from the caller's request or
from the service config; do not paste it into a file.

### Reads that work with the service credential

| Call | Gives you |
| --- | --- |
| `<GET /accounts?email=<email>>` | userId, locale, every linked location with its badge, every device row with `platform` and `notify` |
| `<GET /locations?locationId=<id>&account=<email>>` | that one link and its badge. This is the witness |
| `<GET /actuator/prometheus>` | one pod's counters. See the multi-pod trap |

List the calls that write (in the example, `PUT /sync` and `PUT /topics`). Do not reach for them as reads.

Note any state with **no read endpoint** (in the example, permissions and topics). That gap is why the
last step of an investigation often ends at a database query rather than an HTTP call.

## Witnesses for notification delivery

Rank yours by closeness to what the user is missing. Reach for the first one you can authenticate.

**1. The notification row itself.** `<GET /bff/notifications>` with `<user auth header>`, and
`<GET /bff/notifications/unread-count>` beside it. This is the list the user says is empty, so it is the
real witness. The token comes from `<login endpoint>` or out of the app. Note which auth the endpoint
refuses (in the example, the service credential gets `401` here).

**2. A per-subject counter on the send path,** for example `location.badge` read through
`<GET /locations>` with the service credential. The proxy to use when you have no user token. In the
example, `ReviewService.processNewReview` ends with `badgeService.incAccountsBadge`, which runs *after*
`notificationService.recordForAccounts`, so the badge moving proves a row was written. Per-account and
database backed, therefore consistent across pods.

**3. The push send log line.** The push half only. See Loki below.

### The pair that splits send from read

Witnesses 1 and 2 sit on **opposite sides of the read filter**, which is what makes them worth reading
together. The badge is written on the send path and is not filtered by rights or plan.
`NotificationService.list` filters on `NotificationVisibility.allowedTypes`, from the caller's live
rights and plan. So one probe and two reads:

| Badge | List | The break is |
| --- | --- | --- |
| moves | shows the row | nothing. It works |
| moves | stays empty | the **read filter**: the row exists and the caller's rights or plan hide it |
| flat | stays empty | the **send gate**: no row was ever written, so the filter never ran |

The third line is where permission and topic gates live, and no amount of testing the list will reach
it. Probe with `<the synchronous flag, e.g. "waitUntilFinish": true>` and a fresh unique id, so neither
async timing nor a dedup unique index can explain a flat badge.

## Grafana

`<https://grafana.example.com>`. When the `grafana` MCP server is connected, send the query to the
`grafana-fact-checker` agent from this plugin instead of running it here. Production metrics for the service
carry `<job="notify-service-prod">`. Without the MCP, query the API through the page with the user's
session rather than clicking the UI:

```js
// Prometheus, instant query at a chosen time
const P = async (q, t) => {
  const u = `/api/datasources/proxy/uid/<prometheus-uid>/api/v1/query?query=${encodeURIComponent(q)}` + (t?`&time=${t}`:'');
  const j = await (await fetch(u, {credentials:'include'})).json();
  return j.data.result.map(x => ({...x.metric, v: +x.value[1]}));
};
// Loki, range query
const Q = async (expr, fromNs, toNs) => {
  const u = `/api/datasources/proxy/uid/<loki-uid>/loki/api/v1/query_range?query=${encodeURIComponent(expr)}&start=${fromNs}&end=${toNs}&limit=1000&direction=forward`;
  const j = await (await fetch(u, {credentials:'include'})).json();
  return j.data.result.flatMap(s => s.values);
};
```

Datasource uids: `<prometheus-uid>`, `<loki-uid>`, and any second gateway to the same logs.

Prometheus keeps history, so you can read a counter's value at any past instant. You do not need a
baseline snapshot taken before the probe. Fire first, then read both sides afterwards.

## Metrics that separate gates

Scope every query with `<namespace="notify-service-dev">` or `<environment="development">`.

| Metric | Increments when |
| --- | --- |
| `message_dropped_total{status="permission",type="review"}` | only inside `isAllowedToSend`, so **only the permission gate**, never the topic gate |
| `topic_new_review_total{active="false"}` | a `new_reviews` topic is switched off. One tick per switch, so it timestamps the flip |
| `message_review_total{success="true"\|"false"}` | one per device push attempt |
| `notification_filtered_total{type=...}` | a read of the list hid a type. Empty means nobody called the list endpoint |

In the example, the permission counter is the discriminator for "permission row false" versus "topic
switched off by hand", because `disableTopicIfNotAllowed` makes a false permission also disable the
topic, but not the reverse.

Write down every branch that drops a recipient with **no metric and no log**. In the example, a review
sub-filter (directory or star rating) is silent. Rule such a branch out by probing every value, not by
looking for a signal.

## Loki

Label `<namespace="notify-service-dev">`. The push line carries the recipient:

```
{namespace="<notify-service-dev>"} |= "<Push send by token>"
```

In the example it renders `{code=200, device=<token>, account=<email>, loc=...}`. Tallying `account=`
over a probe window answers "who actually got it" directly, which is usually the finding. Filtering the
same stream with `|= "<email>"` gives one subject's whole history, including `Device update:
active|inactive` and `Device error: ... error=NOT_FOUND`.

## Traps

- **Multi-pod.** Two reads of `/actuator/prometheus` hit different replicas and a counter can drop
  between them. Anything comparative has to go through Grafana.
- **A database datasource that points at the wrong environment.** Note any datasource whose name
  suggests dev but which reads production, or which holds none of the tables you need
  (`<datasource name>` points at `<database>`).
- **Metric name clashes.** Other services may export metrics with the same prefix (in the example,
  `topic_*`). Always scope by namespace or job, or the result is another team's metrics.
- **Many device rows on one test account is normal.** Only rows with `notify: true` are ever pushed to,
  so count those before concluding a push was not sent.
