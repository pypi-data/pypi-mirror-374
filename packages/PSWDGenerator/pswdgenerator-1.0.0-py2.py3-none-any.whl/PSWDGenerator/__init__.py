"""Generator-Password"""
__version__="1.0.0"
import random
import time
Passwords=[]
result=""
print("Use:#Passwords to look you saved passwords...")
print("If empty value in length=10")
while True:
	print("Enter length:")
	length=input("->")
	if length == "#Passwords" or length == "#passwords":
		print(Passwords)
		print("Enter length:")
		length=input("->")
	if length:
		pass
	else:
		length=10
	length=int(length)
	print("Enter numbers or words:Or enter selected combinates{[*]Fast password[normal,number,word]}")
	user=input("->")
	if user:
		pass
	else:
		user="normal"
	if user == "normal":
		user="qwertyuiopasdfghjklzxcvbnm1234567890"
	if user == "number":
		user="1234567890"
	if user == "word":
		user="qwertyuiopasdfghjklzxcvbnm"
	if user =="#Exit" or user =="#exit":
		break
	else:
		pass
	if user == "#Passwords" or user == "#passwords":
		print(Passwords)
	if length > 100:
		print("You want continue?")
		print("You need a powerful device for this action!!!")
		print("Yes/No:")
		a=input()
		if a == "Yes" or a == "yes":
			pass
		elif a == "No" or a == "no": 
			break
		if a =="Yes" or a == "yes":
			pass
		elif a == "No" or a == "no":
			break
		else:
			while True:
				print("Enter Yes/No:")
				a=input()
				if a == "Yes" or a == "yes":
					break
				if a == "No" or a == "no":
					break
		if a == "Yes" or a == "yes":
			pass
		if a == "No" or a == "no":
			break
		
		
		
					
				
	for i in range(0,length):
			randomNumber=random.randint(0,len(user)-1)
			Password=[user]
			result+=Password[0][randomNumber]
	print("You Password".center(60,"-"))
	print(result)
	print("")
	Passwords+=[result]	
	result=""
#Made by DenRom__init__()
#DenRom__--__--__--__--__--__--__$$$