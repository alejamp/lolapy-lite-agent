from lolapy.lola_context import LolaContext
from lolapy.lola_middleware import Middleware


# This is an example of a middleware
class AuthMiddleware(Middleware):
    def process_request(self, session, ctx: LolaContext, req):

        print(">> Auth middleware")

        # Example: Append auth data to the request
        # ----------------------------------------
        # This data is going to be available in the request context
        req['__auth'] = {
            'user_id': '1234',
            'user_name': 'John Doe',
            'phone_number': '+1234567890',
        }
        # ----------------------------------------
        
        # You are able to perform any ctx operation here
        # For example, you can set a timeout
        # ctx.set_timeout(10, '10_seconds_without_message')
        # or send a message to the user:
        # ctx.messanger.send_text_message('Hello from middleware', blend=True)

        # Example: Processing a Client Command
        # ------------------------------------
        event_name = req['event']
        if event_name == 'onClientCommand':
            # extract command name from ['data']['command']
            command_name = req['data']['name']
            command_args = req['data']['args']
            command_is_auth = req['data']['authenticated']

            if command_name == '/phone':
                phone = command_args[0] if len(command_args) > 0 else None
                ctx.messanger.send_text_message('Set phone command detected', blend=False, appendToHistory=False)
                ctx.messanger.send_text_message(f'Setting new phone: {phone}', blend=False, appendToHistory=False)
                return False
        # ------------------------------------


        # Example: Processing a Text Message
        # ------------------------------------
        # extract text from ['data']['message']['text'] dont fail if not present message or text
        text = req['data'].get('message', {}).get('text', None)
        if text == 'skip':
            ctx.messanger.send_text_message('skipping processing this event', blend=False)
            # Note that we are returning False here
            # This will skip the event processing
            # no handlers will be called in assistant code
            return False
        # ------------------------------------

