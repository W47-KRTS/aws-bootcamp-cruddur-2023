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

from lib.cognito_jwt_token import CognitoJwtToken, TokenVerifyError

# HoneyComb ----------
#from opentelemetry import trace
#from opentelemetry.instrumentation.flask import FlaskInstrumentor
#from opentelemetry.instrumentation.requests import RequestsInstrumentor
#from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
#from opentelemetry.sdk.trace import TracerProvider
#from opentelemetry.sdk.trace.export import BatchSpanProcessor
#from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor


# X-RAY ---------------
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

# WATCHTOWER----------- 
import watchtower
import logging
from time import strftime



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
# @xray_recorder.capture('activities_home')
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
# @aws_auth.authentication_required
def data_home():
  access_token = CognitoJwtToken.extract_access_token(request.headers)
  try:
    claims = cognito_jwt_token.verify(access_token)
    # authenicated request
    app.logger.debug('authenicated')
    app.logger.debug(claims)
  except TokenVerifyError as e:
    _ = request.data
    abort(make_response(jsonify(message=str(e)), 401))  
    # unauthenicated request
    app.logger.debug('unauthenicated')

  

  data = HomeActivities.run()

  return data, 200


@app.route("/api/activities/notifications", methods=['GET'])
# @xray_recorder.capture('activities_home')
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
# @xray_recorder.capture('activities_home')
@cross_origin()
def data_activities():
  user_handle  = 'andrewbrown'
  message = request.json['message']
  ttl = request.json['ttl']
  model = CreateActivity.run(message, user_handle, ttl)
  if model['errors'] is not None:
    return model['errors'], 422
  else:
    return model['data'], 200
  return

@app.route("/api/activities/<string:activity_uuid>", methods=['GET'])
@cross_origin()
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
  app.run(debug=True)