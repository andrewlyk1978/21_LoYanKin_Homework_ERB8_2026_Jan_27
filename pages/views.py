from django.shortcuts import render

# Create your views here.



def index (request):
    return render(request, 'pages/index.html')
    # For multitables for mulit databse 
    
    
    # return HttpResponse("<h1>hello</h1>")
    #print(request,'pages/index.html')
    #return render(request, 'pages/index.html')

'''
def about (request):
    doctors=Doctor.objects.order_by("-hire_date")[:3]
    mvp_doctors =Doctor.objects.all().filter(is_mvp=True)
    #print(request,request.path)
    context={"doctors":doctors,"mvp_doctors":mvp_doctors}
    return render(request,'pages/about.html',context)
'''