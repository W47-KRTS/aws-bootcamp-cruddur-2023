from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
from flask import jsonify
from flask import *
import os


# from flask_awscognito import AWSCognitoAuthentication

from services.home_activities import *
from services.user_activities import *
from services.create_activity import *
from services.create_reply import *
from services.search_activities import *
from services.notifications_activities import *
from services.message_groups import *
from services.messages import *
from services.create_message import *
from services.show_activity import *

from lib.cognito_jwt_token import CognitoJwtToken, extract_access_token, TokenVerifyError

#  HoneyComb ----------
#from opentelemetry import trace
#from opentelemetry.instrumentation.flask import FlaskInstrumentor
#from opentelemetry.instrumentation.requests import RequestsInstrumentor
#from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
#from opentelemetry.sdk.trace import TracerProvider
#from opentelemetry.sdk.trace.export import BatchSpanProcessor
#from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

# HoneyComb ---------
# Initialize tracing and an exporter that can send data to Honeycomb
# provider = TracerProvider()
# processor = BatchSpanProcessor(OTLPSpanExporter())
# provider.add_span_processor(processor)

# X-RAY ---------------
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

# CloudWatch Logs ----
import watchtower
import logging


# WATCHTOWER----------- 
# import watchtower
# import logging
from time import strftime

# Rollbar ------
from time import strftime
import os
import rollbar
import rollbar.contrib.flask
from flask import got_request_exception

# Configuring Logger to Use CloudWatch
# LOGGER = logging.getLogger(__name__)
# LOGGER.setLevel(logging.DEBUG)
# console_handler = logging.StreamHandler()
# cw_handler = watchtower.CloudWatchLogHandler(log_group='cruddur')
# LOGGER.addHandler(console_handler)
# LOGGER.addHandler(cw_handler)
# LOGGER.info("some message")

# X-RAY ---------------
# xray_url = os.getenv("AWS_XRAY_URL")
# xray_recorder.configure(service='backend-flask', dynamic_naming=xray_url)

# HoneyComb ----------
# OTEL ----------
# Show this in the logs within the backend-flask app (STDOUT)
#simple_processor = SimpleSpanProcessor(ConsoleSpanExporter())
#provider.add_span_processor(simple_processor)
# Initialize tracing and an exporter that can send data to Honeycomb
#provider = TracerProvider()
#processor = BatchSpanProcessor(OTLPSpanExporter())
#provider.add_span_processor(processor)
#trace.set_tracer_provider(provider)
#tracer = trace.get_tracer(__name__)

app = Flask(__name__)

cognito_jwt_token = CognitoJwtToken(
user_pool_id=os.getenv("AWS_COGNITO_USER_POOL_ID"), 
user_pool_client_id=os.getenv("AWS_COGNITO_USER_POOL_CLINET_ID"), 
region=os.getenv("AWS_DEFAULT_REGION")
)

"""
app.config['AWS_COGNITO_USER_POOL_ID'] = os.getenv("AWS_COGNITO_USER_POOL_ID")
app.config['AWS_COGNITO_USER_POOL_CLINET_ID'] = os.getenv("AWS_COGNITO_USER_POOL_CLINET_ID")

aws_auth = AWSCognitoAuthentication(app)
"""

# X-RAY ---------------
# XRayMiddleware(app, xray_recorder)

# HoneyComb ----------
# Initialize automatic intrumentation with Flask
#FlaskInstrumentor().instrument_app(app)
#RequestsInstrumentor().instrument()

frontend = os.getenv('FRONTEND_URL')
backend = os.getenv('BACKEND_URL')
origins = [frontend, backend]

cors = CORS(
  app, 
  resources={r"/api/*": {"origins": origins}},
  headers=['Content-Type', 'Authorization'], 
  expose_headers='Authorization',
  methods="OPTIONS,GET,HEAD,POST"
)

# CloudWatch Logs -----
#@app.after_request
#def after_request(response):
#    timestamp = strftime('[%Y-%b-%d %H:%M]')
#    LOGGER.error('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)
#    return response

# Rollbar ----------
rollbar_access_token = os.getenv('ROLLBAR_ACCESS_TOKEN')
@app.before_first_request
def init_rollbar():
    """init rollbar module"""
    rollbar.init(
        # access token
        rollbar_access_token,
        # environment name
        'production',
        # server root directory, makes tracebacks prettier
        root=os.path.dirname(os.path.realpath(__file__)),
        # flask already sets up logging
        allow_logging_basic_config=False)

    # send exceptions from `app` to rollbar, using flask's signal system.
    got_request_exception.connect(rollbar.contrib.flask.report_exception, app)

@app.route('/rollbar/test')
def rollbar_test():
    rollbar.report_message('Hello World!', 'warning')
    return "Hello World!"

# WATCHTOWER----------- 
# @app.after_request
# def after_request(response):
#    timestamp = strftime('[%Y-%b-%d %H:%M]')
#    LOGGER.error('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)
#    return response

@app.route("/api/message_groups", methods=['GET'])
def data_message_groups():
  user_handle  = 'andrewbrown'
  model = MessageGroups.run(user_handle=user_handle)
  if model['errors'] is not None:
    return model['errors'], 422
  else:
    return model['data'], 200

@app.route("/api/messages/@<string:handle>", methods=['GET'])
def data_messages(handle):
  user_sender_handle = 'andrewbrown'
  user_receiver_handle = request.args.get('user_reciever_handle')

  model = Messages.run(user_sender_handle=user_sender_handle, user_receiver_handle=user_receiver_handle)
  if model['errors'] is not None:
    return model['errors'], 422
  else:
    return model['data'], 200
  return

@app.route("/api/messages", methods=['POST','OPTIONS'])
@cross_origin()
def data_create_message():
  user_sender_handle = 'andrewbrown'
  user_receiver_handle = request.json['user_receiver_handle']
  message = request.json['message']

  model = CreateMessage.run(message=message,user_sender_handle=user_sender_handle,user_receiver_handle=user_receiver_handle)
  if model['errors'] is not None:
    return model['errors'], 422
  else:
    return model['data'], 200
  return

@app.route("/api/activities/home", methods=['GET'])
# @xray_recorder.capture('activities_home')
def data_home():
  access_token = CognitoJwtToken.extract_access_token(request.headers)
  try:
    claims = cognito_jwt_token.verify(access_token)
    # authenicated request
    app.logger.debug('authenicated')
    app.logger.debug(claims)
    app.logger.debug(claims['username'])
    data = HomeActivities.run(cognito_user_id=claims['username'])
  except TokenVerifyError as e:  
    # unauthenicated request
    app.logger.debug(e)
    app.logger.debug('unauthenicated')
    data = HomeActivities.run()
  return data, 200

@app.route("/api/activities/notifications", methods=['GET'])
def data_notifications():
  data = NotificationsActivities.run()
  return data, 200

@app.route("/api/activities/@<string:handle>", methods=['GET'])
# @xray_recorder.capture('activities_home')
def data_handle(handle):
  model = UserActivities.run(handle)
  if model['errors'] is not None:
    return model['errors'], 422
  else:
    return model['data'], 200

@app.route("/api/activities/search", methods=['GET'])
# @xray_recorder.capture('activities_home')
def data_search():
  term = request.args.get('term')
  model = SearchActivities.run(term)
  if model['errors'] is not None:
    return model['errors'], 422
  else:
    return model['data'], 200
  return

@app.route("/api/activities", methods=['POST','OPTIONS'])
@cross_origin()
def data_activities():
  user_handle  = 'andrewpostu'
  message = request.json['message']
  ttl = request.json['ttl']
  model = CreateActivity.run(message, user_handle, ttl)
  if model['errors'] is not None:
    return model['errors'], 422
  else:
    return model['data'], 200
  return

@app.route("/api/activities/<string:activity_uuid>", methods=['GET'])
@xray_recorder.capture('activities_show')
def data_show_activity(activity_uuid):
  data = ShowActivities.run(activity_uuid=activity_uuid)
  return data, 200

@app.route("/api/activities/<string:activity_uuid>/reply", methods=['POST','OPTIONS'])
@cross_origin()
def data_activities_reply(activity_uuid):
  user_handle  = 'andrewbrown'
  message = request.json['message']
  model = CreateReply.run(message, user_handle, activity_uuid)
  if model['errors'] is not None:
    return model['errors'], 422
  else:
    return model['data'], 200
  return

if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0', port=4567)