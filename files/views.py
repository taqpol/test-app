from rest_framework import permissions, status, authentication
from rest_framework.response import Response
from rest_framework.views import APIView

from files.models import Image

from django.contrib.auth import get_user_model

class FileUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.SessionAuthentication]

    def post(self, request, *args, **kwargs):
        filename_req = request.data.get('filename')
        if not filename_req:
            return Response({"message": "A filename is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not get_user_model().objects.get(name=request.user).is_active:
            return Response({'message': "You don't have permission to do that."}, status=status.HTTP_403_FORBIDDEN)
        # elif filename_req.split('.')[-1] not in ['pdf', 'xlsx', 'xls', 'jpeg', 'jpg', 'png', 'dwf']:
        #     return Response({"message": "Invalid file extension"}, status=status.HTTP_400_BAD_REQUEST)

        policy_expires = int(time.time()+5000)
        user = request.user

        file_obj = Image.objects.create(user=user, name=filename_req)
        file_obj_id = file_obj.id
        upload_start_path = "{username}/{file_obj_id}/".format(
                    username = request.user,
                    file_obj_id=file_obj_id
            )
        _, file_extension = os.path.splitext(filename_req)
        filename_final = "{file_obj_id}{file_extension}".format(
                    file_obj_id= file_obj_id,
                    file_extension=file_extension

                )

        final_upload_path = "{upload_start_path}{filename_final}".format(
                                 upload_start_path=upload_start_path,
                                 filename_final=filename_final,
                            )
        if filename_req and file_extension:
            file_obj.path = final_upload_path
            file_obj.save()

        policy_document_context = {
            "expire": policy_expires,
            "bucket_name": AWS_UPLOAD_BUCKET,
            "key_name": "",
            "acl_name": "private",
            "content_name": "",
            "content_length": 524288000,
            "upload_start_path": upload_start_path,

            }
        policy_document = """
        {"expiration": "2019-01-01T00:00:00Z",
          "conditions": [
            {"bucket": "%(bucket_name)s"},
            ["starts-with", "$key", "%(upload_start_path)s"],
            {"acl": "%(acl_name)s"},

            ["starts-with", "$Content-Type", "%(content_name)s"],
            ["starts-with", "$filename", ""],
            ["content-length-range", 0, %(content_length)d]
          ]
        }
        """ % policy_document_context
        aws_secret = str.encode(AWS_UPLOAD_SECRET_KEY)
        policy_document_str_encoded = str.encode(policy_document.replace(" ", ""))
        url = 'https://{bucket}.s3.amazonaws.com/'.format(
                        bucket=AWS_UPLOAD_BUCKET,
                        region=AWS_UPLOAD_REGION
                        )
        policy = base64.b64encode(policy_document_str_encoded)
        signature = base64.b64encode(hmac.new(aws_secret, policy, hashlib.sha1).digest())
        data = {
            "expires": policy_expires,
            "policy": policy,
            "signature": signature,
            "key": AWS_UPLOAD_ACCESS_KEY_ID,
            "file_bucket_path": upload_start_path,
            "file_id": file_obj_id,
            "filename": filename_final,
            "url": url,
            "username": AWS_USERNAME,
        }
        
        return Response(data, status=status.HTTP_200_OK)

class FileUploadCompleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.SessionAuthentication]

    def post(self, request, *args, **kwargs):
        file_id = request.POST.get('file')
        size = self.request.POST.get('fileSize')
        data = {}
        type_ = self.request.POST.get('fileType')
        if file_id:
            obj = RequestFileItem.objects.get(id=int(file_id))
            obj.size = int(size)
            obj.uploaded = True
            obj.type = type_
            obj.save()
            data['id'] = obj.id
            data['saved'] = True

        if not 'file_object_ids' in request.session:
            request.session['file_object_ids'] = []

        request.session['file_object_ids'].append(obj.id)
        request.session.modified = True

        return Response(data, status=status.HTTP_200_OK)    

file_policy_view = FileUploadView.as_view()
file_upload_complete_view = FileUploadCompleteView.as_view()