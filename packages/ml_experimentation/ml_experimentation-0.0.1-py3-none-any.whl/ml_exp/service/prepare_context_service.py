from sklearn.base import BaseEstimator
from typing import Union

from ml_exp.repository.sklearn_model_repository import SklearnModelRepository
from ml_exp.repository.general_model_repository import GeneralModelRepository
from ml_exp.service.load_model_service import LoadModelService
from ml_exp.model.ml_model import ModelType
from ml_exp.utils.log_config import LogService, handle_exceptions


class PrepareContextService:
    """Load All Models considering different scenarios related with model type and source type (like obj or file)
    """
    __log_service = LogService()
    scores_classifier = ["accuracy", "roc_auc", "precision_recall"]
    scores_regression = ["mae", "mse", "r2"]

    def __init__(self, scores_target: list[str]) -> None:
        self.contexts: dict = {}
        self.scores_target: list[str] = scores_target

        # Repositories
        self.sklearn_repo = SklearnModelRepository()
        self.general_model_repo = GeneralModelRepository()

        # Services
        self.load_model_service_using_sklearn = LoadModelService(self.sklearn_repo)
        self.load_model_service_using_general = LoadModelService(self.general_model_repo)
        self.__logger = self.__log_service.get_logger(__name__)
    
    def _get_ml_models(self):
        return [model["ml_model"] for model in self.contexts.values()]

    def check_if_context_exists(self, context_name: str) -> None:
        if context_name in self.contexts:
            raise ValueError(f"Context '{context_name}' already exists. Please use a different name.")

    def get_contexts(self):
        return self.contexts
    
    def load_ml_model(self,
                   context_name: str,
                   model_trained: Union[str, BaseEstimator]):
        # load model by path 
        if isinstance(model_trained, str): 
            if ".obj" in model_trained or ".pkl" in model_trained:
               ml_model = self.load_model_service_using_sklearn.load_model_by_path(model_path=model_trained,
                                                                                context_name=context_name)
            else:
               ml_model = self.load_model_service_using_general.load_model_by_path(model_path=model_trained,
                                                                                context_name=context_name)
        # load models_objects to combine with model list
        else:
            if isinstance(model_trained, BaseEstimator):
                ml_model = self.load_model_service_using_sklearn.load_model_by_obj(context_name=context_name,
                                                                                   model_obj=model_trained)
            else:
                ml_model = self.load_model_service_using_general.load_model_by_obj(context_name=context_name,
                                                                                   model_obj=model_trained)
        return ml_model 

    @handle_exceptions(__log_service.get_logger(__name__))
    def add_context(self,
                    context_name: str,
                    model_trained: Union[str, BaseEstimator],
                    ref_data_test: str):

        self.check_if_context_exists(context_name)

        ml_model = self.load_ml_model(context_name=context_name,
                                       model_trained=model_trained)

        self.contexts[context_name] = {"ml_model": ml_model, "test_data_name": ref_data_test}

        # check if everything ok adding this model
        try:
            self.validate_all_contexts()
        except ValueError as e:
            del self.contexts[context_name] # remove the model if validation fails before raise
            raise e

    def validate_all_contexts(self):
        """Validates all experiments by checking if all models are of the same type and if the scores_target are valid.
        """
        self.validate_models()
        self.validate_scores_target()

    def validate_models(self):
        """Checks whether all models are classifiers or regressors.

        Raises:
            ValueError: If there are models of different types in the same model list to apply in the experiment
        """
        ml_models = self._get_ml_models()
        if (not all(model.model_type == ModelType.classifier.value for model in ml_models)
            and not all(model.model_type == ModelType.regressor.value for model in ml_models)
            and not any(model.model_type == ModelType.undefined.value for model in ml_models)):
            raise ValueError("models must need all models to be classifiers or regressors and not a mixture of them, so a comparison is not possible.")
    
    def validate_scores_target(self):
        """Checks whether the performance metric exists and whether it makes sense according to the type of Machine Learning model that will be used

        Raises:
            ValueError: If there are models of different types in the same model list to apply in the experiment
        """
        ml_models = self._get_ml_models()
        if isinstance(self.scores_target, str):
            self.scores_target = [self.scores_target]
        # classifier
        if all(model.model_type == ModelType.classifier.value
               for model in ml_models):
            if all([score not in self.scores_classifier for score in self.scores_target]):
                raise ValueError(f"scores_target must be valid between them {self.scores_classifier}")
        # regressor
        elif all(model.model_type == ModelType.regressor.value
               for model in ml_models):
            if all([score not in self.scores_regression for score in self.scores_target]):
                raise ValueError(f"scores_target must be valid between them {self.scores_regression}")
        # all or one of them may be of the undefined model type
        else:
            # verify if some score exists in all possible options
            if all([score not in self.scores_regression and score not in self.scores_classifier for score in self.scores_target]):
                raise ValueError(f"scores_target must be valid between them {self.scores_regression} or {self.scores_classifier}")