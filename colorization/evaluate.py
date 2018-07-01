import tensorflow as tf
from keras import backend as K

from colorization import Colorization
from colorization.training_utils import evaluation_pipeline, \
    checkpointing_system, plot_evaluation, metrics_system

# PARAMETERS
run_id = 'run{}'.format(1)
val_number_of_images = 100
batch_size = 10
batches = val_number_of_images // batch_size
costs = []

# START
sess = tf.Session()
K.set_session(sess)

# Build the network and the various operations
col = Colorization(256)
evaluations_ops = evaluation_pipeline(col, batch_size)
summary_writer = metrics_system(run_id, sess)
saver, checkpoint_paths, latest_checkpoint = checkpointing_system(run_id)

with sess.as_default():
    # Initialize
    sess.run(tf.global_variables_initializer())
    sess.run(tf.local_variables_initializer())

    # Coordinate the loading of image files.
    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(coord=coord)

    # Restore
    if latest_checkpoint is not None:
        print('Restoring from: {}'.format(latest_checkpoint))
        saver.restore(sess, latest_checkpoint)
        print(' done!')
    else:
        print('No checkpoint found in:', checkpoint_paths)

    # Evaluation (epoch=-1 to say that this is an evaluation after training)
    for batch in range(batches):
        print('Batch: {}/{}'.format(batch, batches), run_id)
        res = sess.run(evaluations_ops)
        plot_evaluation(res, run_id, epoch="-1_{}".format(batch))
        print('Batch Cost: {}'.format(res['cost']))
        costs.append(res['cost'])

    print('Average cost: {}'.format(sum(costs)/len(costs)))

    # Finish off the filename queue coordinator.
    coord.request_stop()
    coord.join(threads)
