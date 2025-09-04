# Copyright (c) 2025 LIN XIAO DAO
# Licensed under the MIT License. See LICENSE file in the project root for full license text.

import os
# Close warnings from tensorflow to ensure great experience.
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2" 
from keras.models import Model, load_model
from importlib.resources import files
from numpy.typing import NDArray
import numpy as np

data_path = files("ae_qem")
class Autoencoder:
    """
    Autoencoder wrapper for noise mitigation.

    This class loads a pretrained autoencoder model eagerly.
    The simple ``mitigate`` method is for interal use. For
    researchers requiring for more flexible usage should use
    the ``model`` attribute directly.

    Attributes
    ----------
    model_path : str
        The location of .keras file. The file contains only 
        the structure of our autoencoder.
    chkpoint_name : str
        The name of checkpoint. The naming rule follows by the 
        name of the train dataset, and the default checkpoint is F.
    """
    def __init__(
            self,
            model_path: str = str(data_path/"data/models/"),
            chkpoint_name: str = "F"
    ):
        """ Load our autoencoder model eagerly. """

        print("Loading our autoencoder model...")
        try: # Keras file might be different when saving via v2 or v3 keras SDK.
            self.model = load_model(
                model_path + "/4qubit_1D_origin_softmax_Keras2.keras", 
                compile=False
            )
        except:
            self.model = load_model(
                model_path+"/4qubit_1D_origin_softmax_Keras3.keras",
                compile=False
            )
        self.model.load_weights(str(data_path/f"data/chkpoints/{chkpoint_name}.h5"))
        print(f"Complete loading the pretrained autoencoder training by dataset {chkpoint_name}.")

    def mitigate(self, input_data: NDArray[np.float32]) -> NDArray[np.float32]:
        """
        Mitigation method for measurement outcomes.
        
        Parameters
        ----------
        input_data : NDArray[np.float32] of shape (n_samples, n_features)
            A measurement outcome.
        
        Returns
        -------
        NDArray[np.float32] of shape (n_samples, n_features)
            The measurement outcome after mitigation.
        """
        return self.model.predict(input_data, verbose=0, batch_size=1)
    
