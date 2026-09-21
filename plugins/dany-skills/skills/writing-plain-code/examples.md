# Longer before / after pairs

Read `SKILL.md` for the rules. These show the rules working together on a
whole method, in the three languages Dany reads most.

## Dart: a widget tree split (rules 2, 4, 7)

Before: one `build`, six levels deep, a collection-if and a nested ternary.

```dart
@override
Widget build(BuildContext context) {
  final state = context.watch<PostCubit>().state;
  return Column(
    children: [
      if (state.status == .loading)
        const Center(child: CircularProgressIndicator())
      else
        for (final post in state.posts)
          Padding(
            padding: .all(8),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    children: [
                      Text(post.title),
                      Text(post.isDraft ? 'Draft' : post.isScheduled ? 'Scheduled' : 'Published'),
                    ],
                  ),
                ),
              ],
            ),
          ),
    ],
  );
}
```

After: named locals, plain `if` / `else`, one widget per thing on screen.

```dart
@override
Widget build(BuildContext context) {
  final state = context.watch<PostCubit>().state;
  final isLoading = state.status == .loading;

  if (isLoading) {
    return const Center(child: CircularProgressIndicator());
  }
  return Column(
    children: state.posts.map((post) => PostTile(post: post)).toList(),
  );
}

class PostTile extends StatelessWidget {
  const PostTile({super.key, required this.post});

  final Post post;

  @override
  Widget build(BuildContext context) {
    String statusLabel;
    if (post.isDraft) {
      statusLabel = 'Draft';
    } else if (post.isScheduled) {
      statusLabel = 'Scheduled';
    } else {
      statusLabel = 'Published';
    }

    return Padding(
      padding: .all(8),
      child: Column(
        children: [Text(post.title), Text(statusLabel)],
      ),
    );
  }
}
```

## Kotlin: a scope-function chain (rules 1, 3, 6)

Before:

```kotlin
fun send(request: PushRequest?): Pair<Boolean, String?> =
    request?.takeIf { it.tokens.isNotEmpty() }
        ?.let { req -> client.send(req.tokens, req.payload).also { log.info("sent ${req.tokens.size}") } }
        ?.let { true to it.messageId }
        ?: (false to null)
```

After:

```kotlin
data class SendResult(val wasSent: Boolean, val messageId: String?)

fun send(request: PushRequest?): SendResult {
    if (request == null) return SendResult(wasSent = false, messageId = null)
    if (request.tokens.isEmpty()) return SendResult(wasSent = false, messageId = null)

    val response = client.send(request.tokens, request.payload)
    log.info("sent ${request.tokens.size}")
    return SendResult(wasSent = true, messageId = response.messageId)
}
```

## Swift: a guard rewrite (rules 6, 7)

Before:

```swift
func openInApp() {
    if let id = model.reviewId, !id.isEmpty {
        if session.isReachable && !session.isSending {
            if let data = try? JSONEncoder().encode(["openReview": id]) {
                session.send(data)
            }
        }
    }
}
```

After:

```swift
func openInApp() {
    guard let reviewId = model.reviewId, !reviewId.isEmpty else { return }

    let canSend = session.isReachable && !session.isSending
    guard canSend else { return }

    guard let data = try? JSONEncoder().encode(["openReview": reviewId]) else { return }
    session.send(data)
}
```
