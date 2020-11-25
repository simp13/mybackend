from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from PIL import Image
import face_recognition
import numpy as np 
import base64
import io
import json

# models 
from .models import RegisterFaces,RecognizeLogs
# Create your views here.


def register(faceimage,boxes,name):
    known_faces = []
    known_names = []
    data = RegisterFaces.objects.all()
    encodings = face_recognition.face_encodings(faceimage,boxes)

    for encoding in encodings:
        known_faces.append(encoding)
        known_names.append(name)

    if len(data) > 0 :
        data_obj = data.first()
        new_encodings = data_obj.face_features_names["encodings"] + known_faces
        new_names = data_obj.face_features_names["names"] + known_names
        data_obj.face_features_names = {"encodings": new_encodings,"names": new_names}
        data_obj.save()
    else:
        data_obj = {"encodings": known_faces,"names": known_names}
        try:
            RegisterFaces.objects.create(face_features_names=data_obj)
        except Exception as e:
            pass 

    
@csrf_exempt
def FaceRecogRegister(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('name', None)
        userfaceimagebase64 = data.get('face', None)
        if username is not None and userfaceimagebase64 is not None:
            userface = base64.b64decode(userfaceimagebase64)
            buf = io.BytesIO(userface)
            userfaceimage = np.array(Image.open(buf).convert('RGB'))
            face_locations = face_recognition.face_locations(userfaceimage)
            register(userfaceimage,face_locations,username)
            return JsonResponse({"success": True}, status=200)
        return JsonResponse({"success": False},status=400)

@csrf_exempt
def FaceRecognize(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        userfaceimagebase64 = data.get('face',None)
        if userfaceimagebase64 is not None:
            userface = base64.b64decode(userfaceimagebase64)
            buf = io.BytesIO(userface)
            userfaceimage = np.array(Image.open(buf).convert('RGB'))
            face_locations = face_recognition.face_locations(userfaceimage)
            encodings = face_recognition.face_encodings(userfaceimage,face_locations)
            
            # Face Data From Database 
            data_obj = RegisterFaces.objects.all().first()
            known_faces = data_obj.face_features_names["encodings"]
            known_names = data_obj.face_features_names["names"]

            names = []
            for encoding in encodings:
                matches = face_recognition.compare_faces(known_faces,encoding)
                name = "unknown"
                if True in matches:
                    matchedIdxs = [i for (i,b) in enumerate(matches) if b]
                    counts = {}

                    for i in matchedIdxs:
                        name = known_names[i]
                        counts[name] = counts.get(name,0) + 1

                    name = max(counts,key=counts.get)
                try:
                    RecognizeLogs.objects.create(name=name)
                except Exception as e:
                    pass 
                names.append(name)    
        return JsonResponse({"status": True,"names": names},status=200)
    return JsonResponse({"success": False,"names": []},status=400)
