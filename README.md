# dl4nlp

## Compile PyTorch Slides
```sh
jupyter nbconvert \
  RemoveElements --TagRemovePreprocessor.remove_input_tags=\{\"Output\",\"TensorFlow\"\} \
  RemoveElements --TagRemovePreprocessor.remove_all_outputs_tags=\{\"Input\",\"TensorFlow\"\} \
  --to slides --post serve scratch.ipynb 
````

## Compile TensorFlow Slides
```sh
jupyter nbconvert \
  RemoveElements --TagRemovePreprocessor.remove_input_tags=\{\"Output\",\"PyTorch\"\} \
  RemoveElements --TagRemovePreprocessor.remove_all_outputs_tags=\{\"Input\",\"PyTorch\"\} \
  --to slides --post serve scratch.ipynb 
```