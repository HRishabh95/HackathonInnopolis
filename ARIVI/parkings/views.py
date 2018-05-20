import json
import datetime

from datetime import timedelta

import jwt
from django.contrib.auth import authenticate

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.serializers import JSONWebTokenSerializer


from parkings.utils import *
from .detail_serializers import *
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status

predictor_data_dest = "/Users/mergalievibragim/Desktop/Hackathon/HackathonInnopolis/data.json"

class ParkingView(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ['get']
    renderer_classes = (JSONRenderer,)

    def get(self, request, *args, **kwargs):
        try:
            data = open(predictor_data_dest)
            json_data = json.load(data)
            return Response(json_data)
        except:
            return JSONError(INSTANCE_DOES_NOT_EXIST)



