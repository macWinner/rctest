"""
Usage:
  # From tensorflow/models/
  # Create train data:
  python generate_tfrecord.py --csv_input=images/train_labels.csv --image_dir=images/train --output_path=train.record

  # Create test data:
  python generate_tfrecord.py --csv_input=images/test_labels.csv  --image_dir=images/test --output_path=test.record
"""
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import io
import pandas as pd
import tensorflow as tf

from PIL import Image
from object_detection.utils import dataset_util
from collections import namedtuple, OrderedDict

flags = tf.app.flags
flags.DEFINE_string('csv_input', '', 'Path to the CSV input')
flags.DEFINE_string('image_dir', '', 'Path to the image directory')
flags.DEFINE_string('output_path', '', 'Path to output TFRecord')
FLAGS = flags.FLAGS

'''
# TO-DO replace this with label map
def class_text_to_int(row_label):
    if row_label == 'nine':
        return 1
    elif row_label == 'ten':
        return 2
    elif row_label == 'jack':
        return 3
    elif row_label == 'queen':
        return 4
    elif row_label == 'king':
        return 5
    elif row_label == 'ace':
        return 6
    else:
        None
'''

# TO-DO replace this with label map
def class_text_to_int(row_label):
    if row_label == 'Bengal Adult':
        return 1
    elif row_label == 'British Shorthair Adult':
        return 2
    elif row_label == 'British Shorthair Kitten':
        return 3
    elif row_label == 'Maine Coon Adult':
        return 4
    elif row_label == 'Maine Coon Kitten':
        return 5
    elif row_label == 'Norwegian Forest Adult':
        return 6
    if row_label == 'Persian Adult':
        return 7
    elif row_label == 'Persian Kitten':
        return 8
    elif row_label == 'Siamese Adult':
        return 9
    elif row_label == 'Siberian Adult':
        return 10
    elif row_label == 'Sphynx Adult':
        return 11
    elif row_label == 'Sphynx Kitten':
        return 12
    if row_label == 'Digestive Care':
        return 13
    elif row_label == 'Hair & Skin Care':
        return 14
    elif row_label == 'Hairball Care':
        return 15
    elif row_label == 'Light Weight Care':
        return 16
    elif row_label == 'Oral Care':
        return 17
    elif row_label == 'Urinary Care':
        return 18
    if row_label == 'Ageing 12+':
        return 19
    elif row_label == 'Ageing Sterilised 12+':
        return 20
    elif row_label == 'Aroma Exigent':
        return 21
    elif row_label == 'Fit 32':
        return 22
    elif row_label == 'Indoor 27':
        return 23
    elif row_label == 'Indoor 7+':
        return 24
    if row_label == 'Indoor Appetite Control':
        return 25
    elif row_label == 'Indoor Long Hair':
        return 26
    elif row_label == 'Protein Exigent':
        return 27
    elif row_label == 'Savour Exigent':
        return 28
    elif row_label == 'Sensible 33':
        return 29
    elif row_label == 'Sterilised 37':
        return 30
    if row_label == 'Sterilised 7+':
        return 31
    elif row_label == 'Kitten':
        return 32
    elif row_label == 'Kitten Sterilised':
        return 33
    elif row_label == 'Mother & Babycat':
        return 34
    else:
        None


def split(df, group):
    data = namedtuple('data', ['filename', 'object'])
    gb = df.groupby(group)
    return [data(filename, gb.get_group(x)) for filename, x in zip(gb.groups.keys(), gb.groups)]


def create_tf_example(group, path):
    with tf.gfile.GFile(os.path.join(path, '{}'.format(group.filename)), 'rb') as fid:
        encoded_jpg = fid.read()
    encoded_jpg_io = io.BytesIO(encoded_jpg)
    image = Image.open(encoded_jpg_io)
    width, height = image.size

    filename = group.filename.encode('utf8')
    image_format = b'jpg'
    xmins = []
    xmaxs = []
    ymins = []
    ymaxs = []
    classes_text = []
    classes = []

    for index, row in group.object.iterrows():
        xmins.append(row['xmin'] / width)
        xmaxs.append(row['xmax'] / width)
        ymins.append(row['ymin'] / height)
        ymaxs.append(row['ymax'] / height)
        classes_text.append(row['class'].encode('utf8'))
        classes.append(class_text_to_int(row['class']))

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(filename),
        'image/source_id': dataset_util.bytes_feature(filename),
        'image/encoded': dataset_util.bytes_feature(encoded_jpg),
        'image/format': dataset_util.bytes_feature(image_format),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
    }))
    return tf_example


def main(_):
    writer = tf.python_io.TFRecordWriter(FLAGS.output_path)
    path = os.path.join(os.getcwd(), FLAGS.image_dir)
    examples = pd.read_csv(FLAGS.csv_input)
    grouped = split(examples, 'filename')
    for group in grouped:
        tf_example = create_tf_example(group, path)
        writer.write(tf_example.SerializeToString())

    writer.close()
    output_path = os.path.join(os.getcwd(), FLAGS.output_path)
    print('Successfully created the TFRecords: {}'.format(output_path))


if __name__ == '__main__':
    tf.app.run()
