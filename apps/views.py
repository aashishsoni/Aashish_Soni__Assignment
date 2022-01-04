from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model, authenticate, logout
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.models import UserProfile, sale_statistics
import pandas as pd
from collections import defaultdict


User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny, ])
def signup(request):
    """ new user creation function """
    email = request.data['email']
    password = request.data['password']
    first_name = request.data['first_name']
    last_name = request.data['last_name']
    first_isalpha = password[0].isalpha()
    if len(password) < 8:
        return Response({'status': 'fail', 'message': 'The password must be at least 8 characters long!'})
    if all(c.isalpha() == first_isalpha for c in password):
        return Response({'status': 'fail', 'message': 'The Password must be a combination of characters with '
                                                          'numbers or special characters!'})
    if not User.objects.filter(email=email).exists():
        User.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name)
        return Response({'status': 'success', "message": "user create successfully"})
    return Response({'status': 'fail', "message": "this email is already register"})


@api_view(['POST'])
@permission_classes([AllowAny, ])
def signin(request):
    """ for user login """
    email = request.data['email']
    password = request.data['password']
    if not User.objects.filter(email=email).exists():
        return Response({'status': 'fail', "message": "this email not register"})
    user = User.objects.get(email=email)
    if user.is_active:
        authenticate(email=email, password=password)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'status': 'success', 'message': 'User loggedIn', 'token': token.key, 'user_id':user.id})
    return Response({'status': 'fail', 'message': 'this user is not active'})


@api_view(['POST'])
def user_logout(request):
    try:
        request.user.auth_token.delete()
    except (AttributeError, ObjectDoesNotExist):
        pass
    logout(request)
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def user_details(request, id):
    """ get all user list with his/her detail's """
    user = User.objects.get(id=id)
    all_user_data = UserProfile.objects.get(user=user)
    user_all_data = []
    all_data = {'id':user.id, 'first_name':all_user_data.user.first_name, 'last_name': all_user_data.user.last_name, 'email': all_user_data.user.email}
    user_all_data.append(all_data)
    return Response({'status': 'success', 'message': 'user details', 'data': user_all_data})


@api_view(['GET'])
@permission_classes([AllowAny, ])
def countries(request):
    file_location = "sales_fiels/citymayors.csv"
    df = pd.read_csv(file_location)
    Country = df['Country'].unique()
    rwc_data = []
    counter_data = dict()
    my_dict = defaultdict(list)
    for jdict in df.to_dict(orient='records'):
        my_dict[jdict['Country']].append({"id":int(len(my_dict[jdict['Country']]) + 1),"name": jdict['City']})
    count = 1
    for x in Country:
        if x in my_dict:
            all_data = {'id': count, 'name': x, "cities": my_dict[x]}
            rwc_data.append(all_data)
            count += count
    return Response({'status': 'success', 'message': "user data get successfully", 'data': rwc_data})


@api_view(['POST'])
@permission_classes([AllowAny, ])
def StatisticsData(request):
    date = request.data['date']
    product = request.data['product']
    sales_number = request.data['sales_number']
    revenue = request.data['revenue']
    user_id = request.data['user_id']
    sale_statistics_data = sale_statistics.objects.create(user_id=user_id, date=date, product=product, 
    sales_number=sales_number, revenue=revenue)
    data = {'sale_statistics_data': sale_statistics_data.date, "product" : sale_statistics_data.product,
    "sales_number" : sale_statistics_data.sales_number, "revenue" : sale_statistics_data.revenue}
    return Response({'status': 'success', 'message': "user data get successfully", 'data': data}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def StatisticsAverageData(request):
    # sale_statistics_data = sale_statistics.objects.filter(user=request.user).values_list('revenue').aggregate(Avg('revenue'))
    sale_statistics_data = sale_statistics.objects.filter(user=request.user).values()
    average_data = 0
    try:
        for statistics_data in sale_statistics_data:
            average_data = average_data + statistics_data['revenue']
        average_sales_for_current_user = average_data / len(sale_statistics_data)
    except Exception:
        return Response({'status': 'success', 'message': "user data get successfully", 'average_sales_for_current_user': average_data})
    return Response({'status': 'success', 'message': "user data get successfully", 'average_sales_for_current_user': average_sales_for_current_user})
