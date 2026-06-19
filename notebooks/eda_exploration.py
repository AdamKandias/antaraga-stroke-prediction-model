## Import Libraries

import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import seaborn as sns 
import mplcyberpunk
plt.style.use('cyberpunk') 

## EDA

df =pd.read_csv("healthcare-dataset-stroke-data.csv")
df.head()

df.dtypes

df.isna().sum()

for col in df.columns:
    if df[col].dtype=='object':
        print(col)
        print(df[col].unique())

df.drop('id' , axis = 1 , inplace = True)

df.shape

df.describe().T

df["bmi"] = df["bmi"].fillna(df["bmi"].mean())

df.isna().sum()

## Visualization

sns.pairplot(df,hue="stroke")

numerical_data = df[['age','avg_glucose_level','bmi']]

sns.kdeplot(data=numerical_data)

sns.countplot(x ='stroke' , data = df).set_title('Count of Stroke Patients')

sns.countplot(x='gender', hue='stroke', data=df).set_title('Stroke patients by Gender')

sns.countplot(x='ever_married', hue='stroke', data=df).set_title('Stroke patients By Marital Status')

sns.countplot(x='smoking_status',hue='stroke',data=df).set_title("Stroke Patients By Smoking Status")

sns.countplot(x='work_type',hue='stroke',data=df).set_title("Stroke Patients By Work type")

fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(16, 12))

sns.boxplot(df['age'], ax=axes[0, 0]).set_title("**BoxPlot For Age Col**")
sns.histplot(data=df, x='age', kde=True, ax=axes[0, 1]).set_title("**Distribution Of Age**")
sns.lineplot(data=df, x='age', y="stroke", ax=axes[0, 2]).set_title('**Lineplot For Age with Stroke**')

sns.boxplot(df['avg_glucose_level'], ax=axes[1, 0]).set_title("BoxPlot For Glucose")
sns.histplot(data=df, x='avg_glucose_level', kde=True, ax=axes[1, 1]).set_title("Distribution Of Glucose")
sns.lineplot(data=df, x='avg_glucose_level', y="stroke", ax=axes[1, 2]).set_title('**Lineplot For Glucose Level With Stroke')

sns.boxplot(df['bmi'], ax=axes[2, 0]).set_title("BoxPlot For Bmi Col")
sns.histplot(data=df, x='bmi', kde=True, ax=axes[2, 1]).set_title("Distribution Of Bmi")
sns.lineplot(data=df, x='bmi', y="stroke", ax=axes[2, 2]).set_title('Lineplot For Bmi With Stroke')

plt.tight_layout()
plt.show()

corr = df.select_dtypes(include='number').corr()
plt.figure(figsize=(12,6))
sns.heatmap(corr,annot=True)

## Data PreProcessing 

for col in df.columns:
    if df[col].dtype=='object':
        print(col)
        print(df[col].unique())

from sklearn.preprocessing import LabelEncoder
le=LabelEncoder()
for col in df.columns:
    if df[col].dtype=='object':
        df[col]=le.fit_transform(df[col]) 

df.head()

df.dtypes

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
for col_name in df.columns:
    if df[col_name].nunique() > 5: 
        df[col_name] = scaler.fit_transform(df[[col_name]])


X = df.drop("stroke",axis=1)
y =df['stroke']

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42,shuffle=True)

## Bikin Models 

## Decision Tree Model

from sklearn.tree import DecisionTreeClassifier
dt = DecisionTreeClassifier()
dt.fit(X_train, y_train)

y_pred_dt = dt.predict(X_test)

from sklearn.metrics import accuracy_score
accuracy_using_decision_tree = round(accuracy_score(y_test, y_pred_dt)*100, 2)
print("Model accuracy using Decision Tree: ", accuracy_using_decision_tree, "%")

import sklearn.metrics as mt
sns.heatmap(mt.confusion_matrix(y_pred_dt,y_test),annot = True,fmt = "d")
plt.title("Decision Tree Classifier")
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

## Support Vector Machine 

from sklearn import svm
svm = svm.SVC()
svm.fit(X_train, y_train)

y_pred_svm = svm.predict(X_test)

accuracy_using_svm = round(accuracy_score(y_test, y_pred_svm)*100, 2)
print("Model accuracy using SVM: ", accuracy_using_svm, "%")

sns.heatmap(mt.confusion_matrix(y_pred_svm,y_test),annot = True,fmt = "d")
plt.title("Support Vector Machine")
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

## Logistic Regression

from sklearn.linear_model import LogisticRegression
lr = LogisticRegression()
lr.fit(X_train, y_train)

y_pred_lr = lr.predict(X_test)

accuracy_using_logistic_regression = round(accuracy_score(y_test, y_pred_lr)*100, 2)
print("Model accuracy using Logistic Regression: ", accuracy_using_logistic_regression, "%")

sns.heatmap(mt.confusion_matrix(y_pred_lr,y_test),annot = True,fmt = "d")
plt.title("Logistic Regression")
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()