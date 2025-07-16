---
tags:
- sentence-transformers
- sentence-similarity
- feature-extraction
- dense
- generated_from_trainer
- dataset_size:318
- loss:CosineSimilarityLoss
widget:
- source_sentence: HI
  sentences:
  - PN-00019 | PARKING/REVERSE AID PROX SENSORS for GAGE AND WARNING DEVICE SYSTEM
    > PARKING /REVERSING AIDS | GAGE AND WARNING DEVICE SYSTEM | PARKING /REVERSING
    AIDS | PARKING/REVERSE AID PROX SENSORS | Service | NA | FSS
  - PN-00413 | INSTRUMENT PANEL & COWL WIRING for ELECT DISTRIBUTION AND ELECTRONIC
    CNTRL > ELECTRICAL WIRING/ CIRCUIT PROTECTOR | ELECT DISTRIBUTION AND ELECTRONIC
    CNTRL | ELECTRICAL WIRING/ CIRCUIT PROTECTOR | INSTRUMENT PANEL & COWL WIRING
    | Not Serviced Separately | EI at Supplier | BTP (Buy)
  - PN-00001 | HEAD LAMP / TAIL LAMP WASHERS for BODY SYSTEM > WIPERS AND WASHERS
    | BODY SYSTEM | WIPERS AND WASHERS | HEAD LAMP / TAIL LAMP WASHERS | Not Serviced
    Separately | EI at Supplier - Procured by Supplier | BTP (Make)
- source_sentence: List all controller cooling parts for electrical vehicle drive
    system
  sentences:
  - PN-00018 | COOLANT PUMP & FLOW CONTROL for ELECTRICAL VEHICLE DRIVE SYSTEM > CONTROLLER
    COOLING | ELECTRICAL VEHICLE DRIVE SYSTEM | CONTROLLER COOLING | COOLANT PUMP
    & FLOW CONTROL | Not Required | EI at Mahindra | BTP (Buy)
  - PN-00009 | CLUTCH DISC ASSY for CLUTCH SYSTEM > CLUTCH AND HOUSING | CLUTCH SYSTEM
    | CLUTCH AND HOUSING | CLUTCH DISC ASSY | Not Serviced Separately | NA | BTP (Buy)
  - PN-00485 | FLOOR CONSOLE ASSEMBLY for TRIMS > COCKPIT | TRIMS | COCKPIT | FLOOR
    CONSOLE ASSEMBLY | Not Serviced Separately | EI at Supplier - Procured by Supplier
    | BTP (Buy)
- source_sentence: Find part PN-00002
  sentences:
  - PN-00443 | COOLANT PUMP & FLOW CONTROL for ELECTRICAL VEHICLE DRIVE SYSTEM > CONTROLLER
    COOLING | ELECTRICAL VEHICLE DRIVE SYSTEM | CONTROLLER COOLING | COOLANT PUMP
    & FLOW CONTROL | Service | EI at Mahindra | Not Required
  - PN-00299 | CONTROLLER ELECTRONIC for ELECTRICAL VEHICLE DRIVE SYSTEM > CONTROLLER
    ELECTRIC DRIVE | ELECTRICAL VEHICLE DRIVE SYSTEM | CONTROLLER ELECTRIC DRIVE |
    CONTROLLER ELECTRONIC | Not Required | EI at Mahindra | NA
  - PN-00285 | SIDE MEMBERS for FRAME  MOUNTING SYSTEM > FRAME SUB SYSTEM | FRAME  MOUNTING
    SYSTEM | FRAME SUB SYSTEM | SIDE MEMBERS | Not Required | EI at Supplier | BTP
    (Make)
- source_sentence: Show all parts
  sentences:
  - PN-00469 | BODY SIDE QTR. GLASS-FRAME / MECH for BODY SYSTEM > GLASS FRAMES AND
    MECHANISMS | BODY SYSTEM | GLASS FRAMES AND MECHANISMS | BODY SIDE QTR. GLASS-FRAME
    / MECH | Production And Service | NA | Not Required
  - PN-00018 | COOLANT PUMP & FLOW CONTROL for ELECTRICAL VEHICLE DRIVE SYSTEM > CONTROLLER
    COOLING | ELECTRICAL VEHICLE DRIVE SYSTEM | CONTROLLER COOLING | COOLANT PUMP
    & FLOW CONTROL | Not Required | EI at Mahindra | BTP (Buy)
  - PN-00088 | BRAKE PEDAL ASSY for PEDALS AND CONTROLS > PEDALS | PEDALS AND CONTROLS
    | PEDALS | BRAKE PEDAL ASSY | Production Only | EI at Supplier | NA
- source_sentence: Find part PN-00018
  sentences:
  - PN-00003 | MOTOR DRIVE MODULE for STEERING SYSTEM > FOUR WHEEL STRG ACTUATOR CONTROL
    | STEERING SYSTEM | FOUR WHEEL STRG ACTUATOR CONTROL | MOTOR DRIVE MODULE | Service
    | EI at Supplier - Procured by Supplier | Not Required
  - PN-00018 | COOLANT PUMP & FLOW CONTROL for ELECTRICAL VEHICLE DRIVE SYSTEM > CONTROLLER
    COOLING | ELECTRICAL VEHICLE DRIVE SYSTEM | CONTROLLER COOLING | COOLANT PUMP
    & FLOW CONTROL | Not Required | EI at Mahindra | BTP (Buy)
  - PN-00020 | A/RST SEAT ASSY 3RD ROW for SEATING SYSTEM > SEAT ASSY 3RD ROW | SEATING
    SYSTEM | SEAT ASSY 3RD ROW | A/RST SEAT ASSY 3RD ROW | Production And Service
    | EI at Mahindra | Not Required
pipeline_tag: sentence-similarity
library_name: sentence-transformers
---

# SentenceTransformer

This is a [sentence-transformers](https://www.SBERT.net) model trained. It maps sentences & paragraphs to a 384-dimensional dense vector space and can be used for semantic textual similarity, semantic search, paraphrase mining, text classification, clustering, and more.

## Model Details

### Model Description
- **Model Type:** Sentence Transformer
<!-- - **Base model:** [Unknown](https://huggingface.co/unknown) -->
- **Maximum Sequence Length:** 256 tokens
- **Output Dimensionality:** 384 dimensions
- **Similarity Function:** Cosine Similarity
<!-- - **Training Dataset:** Unknown -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/UKPLab/sentence-transformers)
- **Hugging Face:** [Sentence Transformers on Hugging Face](https://huggingface.co/models?library=sentence-transformers)

### Full Model Architecture

```
SentenceTransformer(
  (0): Transformer({'max_seq_length': 256, 'do_lower_case': False, 'architecture': 'BertModel'})
  (1): Pooling({'word_embedding_dimension': 384, 'pooling_mode_cls_token': False, 'pooling_mode_mean_tokens': True, 'pooling_mode_max_tokens': False, 'pooling_mode_mean_sqrt_len_tokens': False, 'pooling_mode_weightedmean_tokens': False, 'pooling_mode_lasttoken': False, 'include_prompt': True})
  (2): Normalize()
)
```

## Usage

### Direct Usage (Sentence Transformers)

First install the Sentence Transformers library:

```bash
pip install -U sentence-transformers
```

Then you can load this model and run inference.
```python
from sentence_transformers import SentenceTransformer

# Download from the 🤗 Hub
model = SentenceTransformer("sentence_transformers_model_id")
# Run inference
sentences = [
    'Find part PN-00018',
    'PN-00018 | COOLANT PUMP & FLOW CONTROL for ELECTRICAL VEHICLE DRIVE SYSTEM > CONTROLLER COOLING | ELECTRICAL VEHICLE DRIVE SYSTEM | CONTROLLER COOLING | COOLANT PUMP & FLOW CONTROL | Not Required | EI at Mahindra | BTP (Buy)',
    'PN-00003 | MOTOR DRIVE MODULE for STEERING SYSTEM > FOUR WHEEL STRG ACTUATOR CONTROL | STEERING SYSTEM | FOUR WHEEL STRG ACTUATOR CONTROL | MOTOR DRIVE MODULE | Service | EI at Supplier - Procured by Supplier | Not Required',
]
embeddings = model.encode(sentences)
print(embeddings.shape)
# [3, 384]

# Get the similarity scores for the embeddings
similarities = model.similarity(embeddings, embeddings)
print(similarities)
# tensor([[1.0000, 0.5890, 0.6009],
#         [0.5890, 1.0000, 0.5673],
#         [0.6009, 0.5673, 1.0000]])
```

<!--
### Direct Usage (Transformers)

<details><summary>Click to see the direct usage in Transformers</summary>

</details>
-->

<!--
### Downstream Usage (Sentence Transformers)

You can finetune this model on your own dataset.

<details><summary>Click to expand</summary>

</details>
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Dataset

#### Unnamed Dataset

* Size: 318 training samples
* Columns: <code>sentence_0</code>, <code>sentence_1</code>, and <code>label</code>
* Approximate statistics based on the first 318 samples:
  |         | sentence_0                                                                       | sentence_1                                                                         | label                                                         |
  |:--------|:---------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------|:--------------------------------------------------------------|
  | type    | string                                                                           | string                                                                             | float                                                         |
  | details | <ul><li>min: 3 tokens</li><li>mean: 8.74 tokens</li><li>max: 23 tokens</li></ul> | <ul><li>min: 33 tokens</li><li>mean: 50.32 tokens</li><li>max: 83 tokens</li></ul> | <ul><li>min: 0.0</li><li>mean: 0.5</li><li>max: 1.0</li></ul> |
* Samples:
  | sentence_0                                                                                                 | sentence_1                                                                                                                                                                                                                               | label            |
  |:-----------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------|
  | <code>Show all drive half shaft tubes</code>                                                               | <code>PN-00112 | DRIVE HALF SHAFT TUBES for DRIVELINE SYSTEM > DRIVE HALF SHAFTS | DRIVELINE SYSTEM | DRIVE HALF SHAFTS | DRIVE HALF SHAFT TUBES | Service | NA | NA</code>                                                              | <code>1.0</code> |
  | <code>PARKING/REVERSE AID PROX SENSORS for GAGE AND WARNING DEVICE SYSTEM > PARKING /REVERSING AIDS</code> | <code>PN-00019 | PARKING/REVERSE AID PROX SENSORS for GAGE AND WARNING DEVICE SYSTEM > PARKING /REVERSING AIDS | GAGE AND WARNING DEVICE SYSTEM | PARKING /REVERSING AIDS | PARKING/REVERSE AID PROX SENSORS | Service | NA | FSS</code> | <code>1.0</code> |
  | <code>Find part PN-00012</code>                                                                            | <code>PN-00235 | BACKHOE BOOM for EARTH MOVING ATTACHMENT > EXCAVATOR | EARTH MOVING ATTACHMENT | EXCAVATOR | BACKHOE BOOM | Service | EI at Supplier | BTP (Make)</code>                                                                | <code>0.0</code> |
* Loss: [<code>CosineSimilarityLoss</code>](https://sbert.net/docs/package_reference/sentence_transformer/losses.html#cosinesimilarityloss) with these parameters:
  ```json
  {
      "loss_fct": "torch.nn.modules.loss.MSELoss"
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `num_train_epochs`: 1
- `multi_dataset_batch_sampler`: round_robin

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `overwrite_output_dir`: False
- `do_predict`: False
- `eval_strategy`: no
- `prediction_loss_only`: True
- `per_device_train_batch_size`: 8
- `per_device_eval_batch_size`: 8
- `per_gpu_train_batch_size`: None
- `per_gpu_eval_batch_size`: None
- `gradient_accumulation_steps`: 1
- `eval_accumulation_steps`: None
- `torch_empty_cache_steps`: None
- `learning_rate`: 5e-05
- `weight_decay`: 0.0
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `max_grad_norm`: 1
- `num_train_epochs`: 1
- `max_steps`: -1
- `lr_scheduler_type`: linear
- `lr_scheduler_kwargs`: {}
- `warmup_ratio`: 0.0
- `warmup_steps`: 0
- `log_level`: passive
- `log_level_replica`: warning
- `log_on_each_node`: True
- `logging_nan_inf_filter`: True
- `save_safetensors`: True
- `save_on_each_node`: False
- `save_only_model`: False
- `restore_callback_states_from_checkpoint`: False
- `no_cuda`: False
- `use_cpu`: False
- `use_mps_device`: False
- `seed`: 42
- `data_seed`: None
- `jit_mode_eval`: False
- `use_ipex`: False
- `bf16`: False
- `fp16`: False
- `fp16_opt_level`: O1
- `half_precision_backend`: auto
- `bf16_full_eval`: False
- `fp16_full_eval`: False
- `tf32`: None
- `local_rank`: 0
- `ddp_backend`: None
- `tpu_num_cores`: None
- `tpu_metrics_debug`: False
- `debug`: []
- `dataloader_drop_last`: False
- `dataloader_num_workers`: 0
- `dataloader_prefetch_factor`: None
- `past_index`: -1
- `disable_tqdm`: False
- `remove_unused_columns`: True
- `label_names`: None
- `load_best_model_at_end`: False
- `ignore_data_skip`: False
- `fsdp`: []
- `fsdp_min_num_params`: 0
- `fsdp_config`: {'min_num_params': 0, 'xla': False, 'xla_fsdp_v2': False, 'xla_fsdp_grad_ckpt': False}
- `fsdp_transformer_layer_cls_to_wrap`: None
- `accelerator_config`: {'split_batches': False, 'dispatch_batches': None, 'even_batches': True, 'use_seedable_sampler': True, 'non_blocking': False, 'gradient_accumulation_kwargs': None}
- `deepspeed`: None
- `label_smoothing_factor`: 0.0
- `optim`: adamw_torch
- `optim_args`: None
- `adafactor`: False
- `group_by_length`: False
- `length_column_name`: length
- `ddp_find_unused_parameters`: None
- `ddp_bucket_cap_mb`: None
- `ddp_broadcast_buffers`: False
- `dataloader_pin_memory`: True
- `dataloader_persistent_workers`: False
- `skip_memory_metrics`: True
- `use_legacy_prediction_loop`: False
- `push_to_hub`: False
- `resume_from_checkpoint`: None
- `hub_model_id`: None
- `hub_strategy`: every_save
- `hub_private_repo`: None
- `hub_always_push`: False
- `hub_revision`: None
- `gradient_checkpointing`: False
- `gradient_checkpointing_kwargs`: None
- `include_inputs_for_metrics`: False
- `include_for_metrics`: []
- `eval_do_concat_batches`: True
- `fp16_backend`: auto
- `push_to_hub_model_id`: None
- `push_to_hub_organization`: None
- `mp_parameters`: 
- `auto_find_batch_size`: False
- `full_determinism`: False
- `torchdynamo`: None
- `ray_scope`: last
- `ddp_timeout`: 1800
- `torch_compile`: False
- `torch_compile_backend`: None
- `torch_compile_mode`: None
- `include_tokens_per_second`: False
- `include_num_input_tokens_seen`: False
- `neftune_noise_alpha`: None
- `optim_target_modules`: None
- `batch_eval_metrics`: False
- `eval_on_start`: False
- `use_liger_kernel`: False
- `liger_kernel_config`: None
- `eval_use_gather_object`: False
- `average_tokens_across_devices`: False
- `prompts`: None
- `batch_sampler`: batch_sampler
- `multi_dataset_batch_sampler`: round_robin
- `router_mapping`: {}
- `learning_rate_mapping`: {}

</details>

### Framework Versions
- Python: 3.13.4
- Sentence Transformers: 5.0.0
- Transformers: 4.53.1
- PyTorch: 2.7.1+cpu
- Accelerate: 1.8.1
- Datasets: 3.6.0
- Tokenizers: 0.21.2

## Citation

### BibTeX

#### Sentence Transformers
```bibtex
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/1908.10084",
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->