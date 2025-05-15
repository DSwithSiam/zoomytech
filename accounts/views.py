import datetime
from django.core.exceptions import ValidationError
import random
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.email import send_email
from .serializers import CompanyDetailsSerializers, CustomUserSerializer, CustomUserUpdateSerializer
from .models import *
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated




def create_otp():
    number_list = [x for x in range(1, 10)]  
    code_items_for_otp = []
    for i in range(4):
        num = random.choice(number_list)
        code_items_for_otp.append(num)
    otp_string = "".join(str(item)for item in code_items_for_otp)  
    return otp_string



@api_view(['POST'])
@permission_classes([])
def signup(request):
    if request.method == 'POST':
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(defaults= False)
            user.is_active = False

            otp_string = create_otp()
            email_subject = "Confirm Your Email"
            email_body = render_to_string('confirm_email.html', {'OTP' : otp_string})

            # email = EmailMultiAlternatives(email_subject , '', to=[user.email])
            # email.attach_alternative(email_body, "text/html")
            # email.send()

            send_email(
                user_email = user.email, 
                email_subject = email_subject, 
                email_body = email_body
                )

            
            user.otp = otp_string
            user.save()
            company_details = CompanyDetails.objects.create(user = user)
            return Response({"message" : 'A confirmation email has been sent to your inbox.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(["POST"])
@permission_classes([])
def resend_otp(request):
    email = request.data.get('email')
    if not email:
        return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(email=email)
        
        otp_string = create_otp()

        email_subject = "Confirm Your Email"
        email_body = render_to_string('confirm_email.html', {'OTP': otp_string})
        
        # email = EmailMultiAlternatives(email_subject, '', to=[user.email])
        # email.attach_alternative(email_body, "text/html")
        # email.send()

        send_email(
            user_email = user.email, 
            email_subject = email_subject, 
            email_body = email_body
            )

        


        user.otp = otp_string
        user.save()

        return Response({"message": "A new OTP has been sent to your email."}, status=status.HTTP_200_OK)

    except CustomUser.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])  
@permission_classes([])
def activate(request):
    try:
        email = request.data.get('email')
        OTP = request.data.get('otp')
        user = CustomUser.objects.get(email = email)
        if user.otp == OTP:
                
            user.is_active = True
            user.otp = None
            user.save()

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({ 'email': user.email, 'access_token': access_token, 'refresh_token': str(refresh), "message": "Your account has been successfully activated!"}, status=status.HTTP_200_OK)
        return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({"detail": 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        



@api_view(['POST'])
@permission_classes([])
def login(request):
    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email = email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response({'email': user.email, 'access_token': access_token, 'refresh_token': str(refresh), }, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        


@api_view(['POST'])
@permission_classes([])
def custom_token_refresh(request):
    if request.method == 'POST':
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)

            return Response({"access_token": access_token}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    if request.method == "POST":
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):  
    user = request.user  
    if not user:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        image_url = request.build_absolute_uri(user.image.url) if user.image else None
        return Response({
            'username': user.username,
            'email': user.email,
            'image': image_url,
            'full_name': user.full_name
        }, status=status.HTTP_200_OK)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    if request.method == 'PUT':
        serializer = CustomUserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([])
def pass_reset_request(request):
    email = request.data.get("email")
    try:
        user = CustomUser.objects.get(email=email)

        if user.is_active:
            otp_string = create_otp()

            email_subject = "Confirm Your Email"
            email_body = render_to_string('confirm_email.html', {'OTP': otp_string})
           
            # email = EmailMultiAlternatives(email_subject, '', to=[user.email])
            # email.attach_alternative(email_body, "text/html")
            # email.send()

            send_email(
                user_email = user.email, 
                email_subject = email_subject, 
                email_body = email_body
                )


            user.otp = otp_string
            user.save()

            return Response({'message': 'A confirmation email has been sent to your inbox. Please check your email and follow the instructions to reset your password.'}, status=status.HTTP_200_OK)
        
        return Response({'detail': 'Your account is inactive. Please contact support.'}, status=status.HTTP_400_BAD_REQUEST)

    except CustomUser.DoesNotExist:
        return Response({'detail': 'No user found with the provided email address.'}, status=status.HTTP_400_BAD_REQUEST)




@api_view(["POST"])
@permission_classes([])
def reset_request_activate(request):
    email = request.data.get("email")
    user = CustomUser.objects.get(email = email)
    OTP = request.data.get('otp')

    if user.is_active:
        if OTP == user.otp:
            user.otp = None
            user.save()
            return Response({ "detail" : "OTP Activated"}, status=status.HTTP_200_OK)
        return Response("Please Try Again", status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
@permission_classes([])
def reset_password(request):
    email = request.data.get('email')
    new_password = request.data.get('new_password')

    user = CustomUser.objects.get(email=email)

    if not email and not new_password:
        return Response({"detail": "Email and new password are required."}, status=status.HTTP_400_BAD_REQUEST)
    if not user:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
    if user.is_active:
        if user.check_password(new_password):
            return Response({'detail': 'New password cannot be the same as the old password'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password:
            user.set_password(new_password)
            user.save() 
            return Response({'detail': "Password reset successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Password cant be empty'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'detail': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request):
    if request.method == 'DELETE':
        try:
            user = request.user
            user.delete()
            return Response({'message': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_company_details(request):
    user = request.user
    company_instance = CompanyDetails.objects.filter(user = request.user).exists()

    if not company_instance:
        try:
            serializer = CompanyDetailsSerializers(data=request.data)
            if serializer.is_valid():
                serializer.save(user=user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    if company_instance:
        try:
            company_instance = CompanyDetails.objects.get(user = request.user)
            serializer = CompanyDetailsSerializers(company_instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_company_details(request):
    if request.method == 'GET':
        try:
            company_instance, created = CompanyDetails.objects.get_or_create(user=request.user)
            serializer = CompanyDetailsSerializers(company_instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not old_password or not new_password:
        return Response({'detail': 'Both old and new passwords are required'}, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(old_password):
        return Response({'detail': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

    if old_password == new_password:
        return Response({'detail': 'New password cannot be the same as the old password'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()
    return Response({'detail': 'Password changed successfully'}, status=status.HTTP_200_OK)

