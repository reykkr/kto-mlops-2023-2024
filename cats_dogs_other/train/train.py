import boto3
from steps.extraction import extraction_from_annotation_file
from steps.split import random_split_train_evaluate_test_from_extraction
from steps.test import Inference, test_model
from steps.train_and_evaluate import train_and_evaluate_model

s3_client = boto3.client(
    "s3",
    endpoint_url="http://minio-api-reykkr-dev.apps.sandbox-m4.g2pi.p1.openshiftapps.com",
    aws_access_key_id="minio",
    aws_secret_access_key="minio123"
)

working_dir = "./dist"
bucket_name = "cats-dogs-other"
extract, classes = extraction_from_annotation_file(bucket_name,
                                                   "dataset/cats_dogs_others-annotations.json",
                                                   working_dir + "/cats_dogs_others-annotations.json",
                                                   s3_client)

train_dir = working_dir + "/train"
evaluate_dir = working_dir + "/evaluate"
test_dir = working_dir + "/test"

split_ratio_train = 0.8
split_ratio_evaluate = 0.1
split_ratio_test = 0.1

random_split_train_evaluate_test_from_extraction(extract, classes, split_ratio_train,
                                                 split_ratio_evaluate, split_ratio_test,
                                                 train_dir, evaluate_dir, test_dir, bucket_name,
                                                 "dataset/extract/", s3_client)


model_filename = "final_model.h5"
model_plot_filename = "model_plot.png"
batch_size = 64
epochs = 4

# train & evaluate
model_dir = working_dir + "/model"
model_path = model_dir + "/" + model_filename
plot_filepath = model_dir + "/" + model_plot_filename

train_and_evaluate_model(train_dir, evaluate_dir, test_dir, model_dir, model_path,
                         plot_filepath, batch_size, epochs)

# test the model
model_inference = Inference(model_path)

test_model(model_inference, model_dir, test_dir)
