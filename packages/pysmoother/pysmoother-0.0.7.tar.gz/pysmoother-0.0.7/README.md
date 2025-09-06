##pysmoother allows you to - 

1) Fit Univariate Natural Cubic Polynomial Splines. Allowing you to smooth a predictor and measure its effect on a target variable. 
Refer - Page 151, Equation 5.9 ,The Elements of Statistical Learning: Data Mining, Inference, and Prediction. Second Edition February 2009. Trevor Hastie, Robert Tibshirani, Jerome Friedman

2) Fit Generalized Additive Models for p predictors with one target variable y. 
Refer - Page 298, Algorithm 9.1- The Backfitting Algorithm For Additive Model ,The Elements of Statistical Learning: Data Mining, Inference, and Prediction. Second Edition February 2009. Trevor Hastie, Robert Tibshirani, Jerome Friedman

3) Fit the Local Scoring Algorithm for the Additive Logistic Regression Model.
Refer - Page 300, Algorithm 9.2, The Elements of Statistical Learning: Data Mining, Inference, and Prediction. Second Edition February 2009. Trevor Hastie, Robert Tibshirani, Jerome Friedman

4) Fit Local Regression Models to with p predictors. Allowing one to perform smoothing. 
Refer - Page 200, Local Regression in Rp, The Elements of Statistical Learning: Data Mining, Inference, and Prediction. Second Edition February 2009. Trevor Hastie, Robert Tibshirani, Jerome Friedman




Code Demo - 

1) Fit Univariate Natural Cubic Polynomial Splines

ss = SMOOTHING_SPLINES(X[:,i],Y,penalty = 10)
ss.make_expanded_basis()
ss.make_integral_matrix()
ss.generate_coefficients(plot=True)


2) Fit Generalized Additive Models for p predictors with one target variable y. 

smoothing_type = {0:'s',1:'1',2:'s'} ## l = Loess, s = Smoothing Splines
gam = GAM(X,Y,penalty=4,smoothing_type=smoothing_type)
print(gam.fit_additive_models(iterations=15))
print(gam.fitted_func)
print(gam.alpha)
print(gam.resid)

##Your Final Fitted Curve will be gam.alpha + gam.fitted_func
plt.plot(Y)
plt.plot(np.sum(gam.fitted_func,axis=1))
plt.show()


3a) Fit a Weighted Smoothing Spline
wss = WEIGHTED_SMOOTHING_SPLINE(X[:,i],Y,penalty=10,weight=np.ones(len(X)))
wss.make_expanded_basis()
wss.make_integral_matrix()
wss.generate_coefficients(plot=True)

3b) Fit the Local Scoring Algorithm for the Additive Logistic Regression Model.
LGAM = ADDITIVE_LOGISTIC_REGRESSION_MODEL(X,Y,penalty=10)
LGAM.model_fit(iterations=10)





