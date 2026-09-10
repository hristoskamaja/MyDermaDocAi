/// A single Q&A message tied to an [Analysis], as returned by
/// `GET/POST /analyses/<id>/chat/`: `{id, role, content, created_at}`.
enum ChatRole { user, assistant }

class ChatMessage {
  final int id;
  final ChatRole role;
  final String content;
  final String createdAt;

  ChatMessage({
    required this.id,
    required this.role,
    required this.content,
    required this.createdAt,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'] as int,
      role: (json['role'] as String?) == 'ASSISTANT'
          ? ChatRole.assistant
          : ChatRole.user,
      content: json['content'] as String? ?? '',
      createdAt: json['created_at'] as String? ?? '',
    );
  }
}

/// Response shape of `POST /analyses/<id>/chat/`:
/// `{user_message, assistant_message}`.
class ChatExchange {
  final ChatMessage userMessage;
  final ChatMessage assistantMessage;

  ChatExchange({required this.userMessage, required this.assistantMessage});

  factory ChatExchange.fromJson(Map<String, dynamic> json) {
    return ChatExchange(
      userMessage: ChatMessage.fromJson(
        json['user_message'] as Map<String, dynamic>,
      ),
      assistantMessage: ChatMessage.fromJson(
        json['assistant_message'] as Map<String, dynamic>,
      ),
    );
  }
}
