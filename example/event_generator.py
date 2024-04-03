
import copy


msg_template = {
    'event': 'onTextMessage',
    'lead': {
        'tenantId': 'finco1fgqvcCW7ZOmasd', 
        'assistantId': 'oS8Mm8Gs65P3tT79den1gX', 
        'channelSource': 'chatwoot', 
        'accountId': 4, 
        'inboxId': 114, 
        'inboxName': 'Finconecta Bancacao', 
        'inboxSource': 'whatsapp', 
        'conversationId': 126, 
        'botName': 'Finconecta Bancacao Dev', 
        'signature': 'b94fb87290540a925a87a74c5bd3460cafff68cf2526d42ad4139ef150e06318', 
        'metadata': {
            'id': '1424', 
            'name': 'Christian', 
            'avatarUrl': '', 
            'phone': '+54911408157301', 
            'metadata': {}, 
            'email': None
            }
    },
    'data': { 
        'message': {
            'type': 'message', 
            'lead': {
                'tenantId': 'finco1fgqvcCW7ZOmasd', 
                'assistantId': 'oS8Mm8Gs65P3tT79den1gX', 
                'channelSource': 'chatwoot', 
                'accountId': 4, 
                'inboxId': 114, 
                'inboxName': 'Finconecta Bancacao', 
                'inboxSource': 'whatsapp', 
                'conversationId': 126, 
                'botName': 'Finconecta Bancacao Dev', 
                'signature': 'b94fb87290540a925a87a74c5bd3460cafff68cf2526d42ad4139ef150e06318', 
                'metadata': {
                    'id': '1424', 
                    'name': 'Christian', 
                    'avatarUrl': '', 
                    'phone': '+54911408157301', 
                    'metadata': {}, 
                    'email': None
                    }
            }, 
            'text': 'Puedo sacar un préstamos', 
            'from': {
                'id': '1424', 
                'name': 'Christian', 
                'avatarUrl': '', 
                'phone': '+54911408157301', 
                'metadata': {}, 
                'email': None
            }, 
            'to': {
                'id': 'lola', 
                'name': 'Finconecta Bancacao Dev', 
                'metadata': {}
            }, 
            'metadata': {
                'account': {
                    'id': 4, 
                    'name': 'Development'
                    }, 
                'additional_attributes': {}, 
                'content_attributes': {}, 
                'content_type': 'text', 
                'content': 'Puedo sacar un préstamos', 
                'conversation': {
                    'additional_attributes': {}, 
                    'can_reply': True, 
                    'channel': 'Channel::Whatsapp', 
                    'contact_inbox': {
                        'id': 1488, 
                        'contact_id': 1424, 
                        'inbox_id': 114, 
                        'source_id': '54911408157301', 
                        'created_at': '2024-01-30T17:22:00.632Z', 
                        'updated_at': '2024-01-30T17:22:00.632Z', 
                        'hmac_verified': False, 
                        'pubsub_token': 'mYRitcfq8mC72DT2xmy5RRbg'
                    }, 
                    'id': 126, 
                    'inbox_id': 114, 
                    'messages': [
                        {
                            'id': 140920, 'content': 'Puedo sacar un préstamos', 
                            'account_id': 4, 
                            'inbox_id': 114, 
                            'conversation_id': 126, 
                            'message_type': 0, 
                            'created_at': 1706798911, 
                            'updated_at': '2024-02-01T14:48:31.967Z', 
                            'private': False, 
                            'status': 'sent', 
                            'source_id': 'wamid.HBgNNTQ5MTE0MDgxNTczNhUCABIYFDNBOTg3NzIyNzhBQTZBMzc4MjJCAA==', 
                            'content_type': 'text', 
                            'content_attributes': {}, 
                            'sender_type': 'Contact', 
                            'sender_id': 1424, 
                            'external_source_ids': {}, 
                            'additional_attributes': {}, 
                            'processed_message_content': 'Puedo sacar un préstamos', 
                            'conversation': {
                                'assignee_id': None, 
                                'unread_count': 2, 
                                'last_activity_at': 1706798911
                                }, 
                            'sender': {
                                'additional_attributes': {}, 
                                'custom_attributes': {}, 
                                'email': None, 
                                'id': 1424, 
                                'identifier': None, 
                                'name': 'Christian', 
                                'phone_number': '+54911408157301', 
                                'thumbnail': '', 'type': 'contact'
                                }
                        }
                    ], 
                    'labels': [], 
                    'meta': {
                        'sender': {
                            'additional_attributes': {}, 
                            'custom_attributes': {}, 
                            'email': None, 'id': 1424, 
                            'identifier': None, 
                            'name': 'Christian', 
                            'phone_number': '+54911408157301', 
                            'thumbnail': '', 'type': 'contact'
                            }, 
                        'assignee': None, 
                        'team': None, 
                        'hmac_verified': False
                    }, 
                    'status': 'pending', 
                    'custom_attributes': {}, 
                    'snoozed_until': None, 
                    'unread_count': 2, 
                    'first_reply_created_at': None, 
                    'priority': None, 
                    'agent_last_seen_at': 1706647642, 
                    'contact_last_seen_at': 0, 
                    'timestamp': 1706798911, 
                    'created_at': 1706635320
                }, 
                'created_at': '2024-02-01T14:48:31.967Z', 
                'id': 140920, 
                'inbox': {
                    'id': 114, 
                    'name': 'Finconecta Bancacao'
                }, 
                'message_type': 'incoming', 
                'private': False, 
                'sender': {
                    'account': {
                        'id': 4, 
                        'name': 'Development'
                    }, 
                    'additional_attributes': {}, 
                    'avatar': '', 
                    'custom_attributes': {}, 
                    'email': None, 
                    'id': 1424, 
                    'identifier': None, 
                    'name': 'Christian', 
                    'phone_number': '+54911408157301', 
                    'thumbnail': ''
                }, 
                'source_id': 'wamid.HBgNNTQ5MTE0MDgxNTczNhUCABIYFDNBOTg3NzIyNzhBQTZBMzc4MjJCAA==', 
                'event': 'message_created'
            }, 
            'attachments': []
        }
    }
}
# -------------------------------------------------------------

def gen_event(signature: None):
    # clone the template
    e = copy.deepcopy(msg_template)
    # set the signature if provided
    if signature:
        e['lead']['signature'] = signature
    
    return e