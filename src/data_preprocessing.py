import os
import pandas as pd
import numpy as np
from src.logger import get_logger
from src.custom_exception import CustomException
from config.path_config import *
from utils.common_functions import read_yaml, load_data
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE

logger = get_logger(__name__)

class DataProcessor:
    # initialization
    def __init__(self, train_path, test_path, processed_dir, config_path):
        self.train_path = train_path
        self.test_path = test_path
        self.processed_dir = processed_dir

        self.config = read_yaml(config_path)

        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)
    
    # Preprocessing data
    def preprocess_data(self, df):
        try:
            logger.info("Starting Data Processing Step")
            # Data Cleaning
            logger.info("Dropping the columns")
            df.drop(columns=['Unnamed: 0', 'Booking_ID'], inplace=True)
            df.drop_duplicates(inplace=True)

            cat_cols = self.config["data_processing"]["categorical_columns"]
            num_cols = self.config["data_processing"]["numerical_columns"]


            logger.info("Applying Label Encoding")
            label_encoder = LabelEncoder()
            mappings = {}
            # Label Encoding -> text to number
            for col in cat_cols:
                df[col] = label_encoder.fit_transform(df[col])
                # Mapping Storage -> Penting untuk production deployment, butuh decode predictions kembali ke text
                mappings[col] = {label:code for label, code in zip(label_encoder.classes_ , label_encoder.transform(label_encoder.classes_))} 

            logger.info("Label Mappings are : ")
            for col, mapping in mappings.items():
                logger.info(f"{col} : {mapping}")

            # skewness handling
            logger.info("Doing Skewness Handling")
            skew_treshold = self.config["data_processing"]["skewness_treshold"]
            skewmess = df[num_cols].apply(lambda x:x.skew())
            # log transformation -> membuat data lebih terdistribusi dengan normal
            for column in skewmess[skewmess>skew_treshold].index:
                df[column] = np.log1p(df[column])

            return df
        except Exception as e:
            logger.error(f"Error during preprocess step {e}")
            raise CustomException("Error while preprocess data", e)
     # Balancing Data   
    def balance_data(self, df):
        try:
            logger.info("Handling Imbalanced Data")
            X = df.drop(columns="booking_status")
            y = df["booking_status"]
            # Oversampling technique
            smote = SMOTE(random_state=42)
            X_resampled , y_resampled = smote.fit_resample(X,y)

            balanced_df = pd.DataFrame(X_resampled, columns=X.columns)
            balanced_df["booking_status"] = y_resampled

            logger.info("Data banaced successfully")
            return balanced_df
        
        except Exception as e:
            logger.error(f"Error during balancing data step {e}")
            raise CustomException("Error while balancing data", e)
    # Feature Selection
    def select_feature(self, df):
        try:
            logger.info("Starting feature selection step")
            X = df.drop(columns="booking_status")
            y = df["booking_status"]

            model = RandomForestClassifier(random_state=42)
            model.fit(X,y)

            feature_importance = model.feature_importances_
            feature_importance_df = pd.DataFrame({
                'feature': X.columns,
                'importance':feature_importance
            })
            
            top_feature_importance_df = feature_importance_df.sort_values(by="importance" , ascending=False)

            num_features_to_select = self.config["data_processing"]["no_of_features"]

            top_10_features = top_feature_importance_df["feature"].head(num_features_to_select).values
            
            top_10_df = df[top_10_features.tolist() + ["booking_status"]]
            
            logger.info(f"Features selected: {top_10_df}")

            logger.info("Feature selection step completed successfully")

            return top_10_df

        except Exception as e:
            logger.error(f"Error during selecting feature step {e}")
            raise CustomException("Error while balancing data", e)
            
    def save_data(self, df, file_path):
        try:
            logger.info("Saving data in processed folder")

            df.to_csv(file_path, index=False)

            logger.info(f"Data saved successfully to {file_path}")

        except Exception as e:
            logger.error(f"Error during saving data step {e}")
            raise CustomException("Error while saving data", e)
     # Data Pipeline   
    def process(self):
        try:
            logger.info("Loading data from RAW directory")

            train_df = load_data(self.train_path)
            test_df = load_data(self.test_path)

            train_df = self.preprocess_data(train_df)
            test_df = self.preprocess_data(test_df)
            
            train_df = self.balance_data(train_df)
            test_df = self.balance_data(test_df)

            train_df = self.select_feature(train_df)
            test_df = test_df[train_df.columns]

            self.save_data(train_df,PROCESSED_TRAIN_DATA_PATH)
            self.save_data(test_df,PROCESSED_TEST_DATA_PATH)

            logger.info("Data processing completed successfully")

        except Exception as e:
            logger.error(f"Error during preprocessing pipeline step {e}")
            raise CustomException("Error while data preprocessing pipeline", e)
        

if __name__ == "__main__":
    processor = DataProcessor(TRAIN_FILE_PATH,TEST_FILE_PATH, PROCESSED_DIR, CONFIG_PATH)
    processor.process()
    