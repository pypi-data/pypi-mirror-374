import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sympy import Matrix, symbols, integrate, Heaviside , lambdify
from scipy.integrate import quad
from sklearn.preprocessing import StandardScaler



class WEIGHTED_SMOOTHING_SPLINE:

	def __init__(self,X,Y,penalty,weight):
		self.X = X
		self.Y = Y
		self.penalty = penalty
		self.weight = np.diag(weight)
		self.y_hat = None
		self.H = None
		self.unique_points = np.unique(self.X)
		self.unique_points[-1] = self.unique_points[-1] - 0.05*(self.unique_points[-1] - self.unique_points[-2])
		self.omega = None


	def apply_basis_functions(self,x):
		res = []
		res.append(1)
		res.append(x)
		res.append(x*x)

		for i in self.unique_points:
			i = float(i)

			if x>=i:
				res.append((x-i)**3)
			else:
				res.append(0)
		return res


	def make_expanded_basis(self):
		res = []
		for i in self.X:
			i = float(i)
			res_val = self.apply_basis_functions(i)
			res.append(res_val)
			

		res = np.array(res)

		self.H = res

	def make_integral_matrix(self):
		t = symbols('t')
		x = [0.01,0.01,2]
		for i in self.unique_points:
			x.append(Heaviside(6*(t-i)))
		x = Matrix(x)
		derivative_matrix = x * x.T

		self.omega = np.zeros((len(x),len(x)))

		for i in range(len(x)):
			for j in range(i,len(x)):
				integrand_func = derivative_matrix[i,j]
				integrand_val = lambdify(t,integrand_func,'numpy')
				result_,error_ = quad(integrand_val,self.unique_points[0],self.unique_points[-1])
				self.omega[i,j] = result_
				if i!=j:
					self.omega[j,i] = result_

		return self.omega




	def generate_coefficients(self,plot = True):



		val = self.H.T.dot(self.weight)
		val = val.dot(self.H)
		val = val + self.penalty * self.omega
		val = np.linalg.inv(val)
		val = val.dot(self.H.T)
		val = val.dot(self.weight)
		val = val.dot(self.Y)
		self.y_hat = self.H.dot(val)

		if plot:
			plt.scatter(self.X,self.Y)
			plt.plot(self.X,self.y_hat)
			plt.show()



class ADDITIVE_LOGISTIC_REGRESSION_MODEL:

	def __init__(self,X,Y,penalty):
		self.X = X
		self.Y = Y
		self.alpha = np.log((np.sum(self.Y)/self.Y.shape[0]) / ( 1- (np.sum(self.Y)/self.Y.shape[0]) )) * np.ones(self.Y.shape[0])
		self.fitted_func = np.zeros((self.X.shape[0],self.X.shape[1]))
		self.neta = self.alpha + np.sum(self.fitted_func,axis=1)
		self.prob = 1/(np.exp(self.neta*-1) + 1)
		self.target = self.neta + ((self.Y - self.prob)/(self.prob * (1-self.prob)))
		self.data_weight = self.prob*(1-self.prob)
		self.penalty = penalty


	def model_fit(self,iterations):
		itr = 0
		num_predictors = self.X.shape[1]

		while itr < iterations:
			for i in range(num_predictors):
				col_select = []
				for j in range(num_predictors):
					if i!=j:
						col_select.append(j)
				
				residuals = self.target - self.alpha -  np.sum(self.fitted_func[:,col_select],axis=1)
				wss = WEIGHTED_SMOOTHING_SPLINE(self.X[:,i],residuals,self.penalty,self.data_weight)
				wss.make_expanded_basis()
				wss.make_integral_matrix()
				wss.generate_coefficients(plot=False)
				self.fitted_func[:,i] = wss.y_hat  - np.mean(wss.y_hat)

			current_fit_resid = np.sum((self.target - self.alpha - np.sum(self.fitted_func,axis=1))**2)
			self.neta = self.alpha + np.sum(self.fitted_func,axis=1)
			self.prob = 1/(np.exp(self.neta*-1) + 1)
			self.target = self.neta + ((self.Y - self.prob)/(self.prob * (1-self.prob)))
			self.data_weight = self.prob*(1-self.prob)
			itr = itr+1
			print(current_fit_resid)





		



class SMOOTHING_SPLINES:

	def __init__(self,X,Y,penalty):
		self.X = X
		self.Y = Y
		self.unique_points = np.unique(self.X)
		self.unique_points[-1] = self.unique_points[-1] - 0.05*(self.unique_points[-1]-self.unique_points[-2]) 
		self.H = None
		self.omega = None
		self.penalty = penalty
		self.y_hat = None


	def apply_basis_functions(self,x):
		res = []
		res.append(1)
		res.append(x)
		res.append(x*x)
		

		for i in self.unique_points:
			i = float(i)
			if x>=i:
				res.append((x-i)**3)
			else:
				res.append(0)
		return res


	def make_expanded_basis(self):
		res = []
		for i in self.X:
			i = float(i)
			val = self.apply_basis_functions(i)
			res.append(val)
		res = np.array(res)
		self.H = res


	def make_integral_matrix(self):
		t = symbols('t')
		x = [0.01,0.01,2]
		for i in self.unique_points:
			x.append( Heaviside(6*(t-i)))
		x = Matrix(x)
		derivative_matrix = x * x.T
		result_matrix = np.zeros((len(x),len(x)))
		for i in range(len(x)):
			for j in range(i,len(x)):
				integrand_func = derivative_matrix[i,j]
				integrand_val = lambdify(t,integrand_func,'numpy')
				result_,error_ = quad(integrand_val,self.unique_points[0],self.unique_points[-1])
				
				result_matrix[i,j] = result_
				if i!=j:
					result_matrix[j,i] = result_matrix[i,j]
		self.omega = result_matrix
		return self.omega




	def generate_coefficients(self,plot = True):
		val = self.H.T.dot(self.H)
		val = val + (self.penalty * self.omega)
		val = np.linalg.inv(val)
		val = val.dot(self.H.T)
		val = val.dot(self.Y)
		self.y_hat = self.H.dot(val)

		if plot:
			plt.scatter(self.X,self.Y)
			plt.plot(self.X,self.y_hat)
			plt.show()

		


class LOESS:

	def __init__(self,X,Y,lbd):
		self.X = X
		self.Y = Y
		self.lbd = lbd

		self.error = None


		ss = StandardScaler()
		ss.fit(self.X)
		self.X_scaled = ss.transform(self.X)

		

		self.Y_smooth = np.zeros((self.Y.shape[0]))



	def kernel_weights(self,index):
		x0_arr = np.ones((self.X_scaled.shape[0],self.X_scaled.shape[1]))
		x0_arr = np.multiply(x0_arr,self.X_scaled[index])
		d = self.X_scaled - x0_arr
		d = d**2
		d = np.sum(d,axis=1)
		d = d/(self.lbd*np.mean(d))
		d = (1 - d*d)*0.75
		d[d<0] = 0
		d = d/np.sum(d)
		weight_matrix = np.diag(d[0:])

		return weight_matrix


	def weighted_LR(self,index):
		weight_val = self.kernel_weights(index)
		val = self.X_scaled.T.dot(weight_val)
		val = val.dot(self.X_scaled)
		val = np.linalg.inv(val)
		val = val.dot(self.X_scaled.T)
		val = val.dot(weight_val)
		val = val.dot(self.Y)
		# print(val.shape)
		smooth_val = self.X_scaled[index,:].dot(val)
		# print(smooth_val)
		self.Y_smooth[index] = smooth_val
		return val

	def LOESS_FIT(self):
		for i in range(self.X.shape[0]):
			self.weighted_LR(i)
		self.error = np.sum((self.Y - self.Y_smooth)**2)
		return self.Y_smooth


	def least_error_lambda(self):
		error_val = []
		for i in range(10,200):
			i = i/100
			loess = LOESS(X,Y,i)
			loess.LOESS_FIT()
			error_val.append([i,float(loess.error)])

		error_val.sort(key = lambda x:x[1])

		return error_val[0]





class GAM:

	def __init__(self,X,Y,penalty,smoothing_type):
		self.X = X
		self.Y = Y
		self.penalty = penalty
		self.fitted_func = None
		self.alpha = None
		self.resid = []
		self.smoothing_type = smoothing_type
		if len(self.smoothing_type.keys())!=self.X.shape[1]:
			return "Enter Smoothing Type For Each Feature"



	def fit_additive_models(self,iterations):
		self.alpha = np.mean(self.Y)*np.ones(self.Y.shape[0])
		num_predictors = self.X.shape[1]
		self.fitted_func = np.zeros((self.X.shape[0],self.X.shape[1]))
		itr = 0
	
		while itr<iterations:
			print(itr)
		
			for i in range(num_predictors):
				col_select = []
				for j in range(num_predictors):
					if j!=i:
						col_select.append(j)
				residuals = self.Y - self.alpha - np.sum(self.fitted_func[:,col_select],axis=1)

				if self.smoothing_type[i]=='s'.lower():
					ss = SMOOTHING_SPLINES(self.X[:,i],residuals,self.penalty)
					ss.make_expanded_basis()
					ss.make_integral_matrix()
					ss.generate_coefficients(plot=False)
					self.fitted_func[:,i] = ss.y_hat  - np.mean(ss.y_hat)

				elif self.smoothing_type[i]=='l'.lower():
					print(residuals)
					loess_input = self.X[:,i]
					loess_input = loess_input.reshape(loess_input.shape[0],1)
					loess = LOESS(loess_input,residuals,0.1)
					loess.LOESS_FIT()
					self.fitted_func[:,i] = loess.Y_smooth  - np.mean(loess.Y_smooth)

				
			current_fit_resid = np.sum((self.Y - self.alpha - np.sum(self.fitted_func,axis=1))**2)
			print(current_fit_resid)
			self.resid.append(current_fit_resid)
			itr = itr+1


