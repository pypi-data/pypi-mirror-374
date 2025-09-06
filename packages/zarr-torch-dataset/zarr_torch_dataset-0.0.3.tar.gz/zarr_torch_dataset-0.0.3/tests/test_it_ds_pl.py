import os

import lightning
import lightning.pytorch.callbacks
import numpy as np
from torch import nn, optim

import tests.utils
from zarrdataset import ZarrDataLoader, ZarrIterableDataset

_ENCODER = nn.Sequential(nn.Linear(4*1024*720, 64), nn.ReLU(), nn.Linear(64, 3))
_DECODER = nn.Sequential(nn.Linear(3, 64), nn.ReLU(), nn.Linear(64, 4*1024*720))


class AutoEncoder(lightning.LightningModule):
    def __init__(self, encoder, decoder):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder

    def _compute_loss(self, batch):
        x = batch
        x = x.view(x.size(0), -1)
        z = self.encoder(x)
        x_hat = self.decoder(z)
        loss = nn.functional.mse_loss(x_hat, x)
        return loss

    def training_step(self, batch, batch_idx):
        return self._compute_loss(batch)

    def validation_step(self, batch, batch_idx):
        loss = self._compute_loss(batch)
        self.log(name='val_loss', value=loss, prog_bar=True, on_epoch=True, on_step=False,
                 sync_dist=True)  # The last parameter is very important in multiprocessing context.

    def configure_optimizers(self):
        optimizer = optim.Adam(self.parameters(), lr=1e-3)
        return optimizer

def test_pytorch_lightning() -> None:
    autoencoder = AutoEncoder(_ENCODER, _DECODER)
    print('> open dataset')
    samples, _ = tests.utils.open_dataset()
    print(f'> {samples.shape=}')
    print('> create dataset and dataloader')

    # Train on all the chunks excepted The first three for the validation.
    chunks_indexes = np.arange(samples.nchunks)
    train_chunk_indexes = chunks_indexes[3:]
    val_chunk_indexes = chunks_indexes[0:3]
    train_ds = ZarrIterableDataset(samples=samples, targets=None,
                                   selected_chunk_indexes=train_chunk_indexes,
                                   shuffle_chunks=True,
                                   chunks_shuffle_seed=1,
                                   shuffle_buffer=True,
                                   buffer_shuffle_seed=2)
    val_ds = ZarrIterableDataset(samples=samples, targets=None,
                                 selected_chunk_indexes=val_chunk_indexes,
                                 shuffle_chunks=False,
                                 shuffle_buffer=False)
    train_da = ZarrDataLoader(dataset=train_ds,
                              num_workers=2,
                              batch_size=64,
                              multiprocessing_context='fork',
                              pin_memory=True,
                              prefetch_factor=2,
                              drop_last=False)
    val_da = ZarrDataLoader(dataset=val_ds,
                            num_workers=1,
                            batch_size=64,
                            multiprocessing_context='fork',
                            pin_memory=True,
                            prefetch_factor=2,
                            drop_last=False)
    timer = lightning.pytorch.callbacks.Timer()
    trainer = lightning.Trainer(max_epochs=3,
                                devices=int(os.environ['SLURM_GPUS_ON_NODE']),
                                num_nodes=int(os.environ['SLURM_NNODES']),
                                strategy='ddp',
                                callbacks=[timer])
    trainer.fit(model=autoencoder, train_dataloaders=train_da, val_dataloaders=val_da)
    print(f'train elapsed time: {tests.utils.display_duration(timer.time_elapsed("train"))}')
    print(f'validation elapsed time: {tests.utils.display_duration(timer.time_elapsed("validate"))}')

if __name__ == '__main__':
    #tests.utils.set_logging_config()
    if tests.utils.DATASET_PATH.exists():
        test_pytorch_lightning()
        print('> done')
        exit(0)
    else:
        print('> create dataset')
        tests.utils.create_dataset()
        print('> done')
        exit(-1)
