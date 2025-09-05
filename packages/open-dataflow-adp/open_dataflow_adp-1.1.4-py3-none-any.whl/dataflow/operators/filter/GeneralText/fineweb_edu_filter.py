from dataflow.operators.eval import FineWebEduScorer
from dataflow.core import OperatorABC
from dataflow.utils.storage import DataFlowStorage
from dataflow.utils.registry import OPERATOR_REGISTRY
from dataflow.utils.utils import get_logger

@OPERATOR_REGISTRY.register()
class FineWebEduFilter(OperatorABC):
    def __init__(self, min_score: float = 2.5, max_score: float = 10000, model_cache_dir: str = './dataflow_cache', device: str = 'cuda'):
        self.min_score = min_score
        self.max_score = max_score
        self.logger = get_logger()
        self.scorer = FineWebEduScorer(model_cache_dir=model_cache_dir, device=device)
        self.filter_name = 'FineWebEduFilter'
        self.logger.info(f"Initializing {self.filter_name} with min_score = {self.min_score}, max_score = {self.max_score}, "
                         f"device = {device}, model_cache_dir = {model_cache_dir}")

    @staticmethod
    def get_desc(lang: str = "zh"):
        return "基于FineWebEduScorer打分器的得分对数据进行过滤。Fineweb-Edu是一个用于评估文本教育价值的分类器，高分表示文本具有较高的教育价值。" if lang == "zh" else "Filter data using scores from the FineWebEduScorer. Fineweb-Edu is a classifier for educational value; higher scores indicate more educational content."

    def run(self, storage: DataFlowStorage, input_key: str, output_key: str='FinewebEduScore'):
        self.input_key = input_key
        self.output_key = output_key
        dataframe = storage.read("dataframe")
        self.logger.info(f"Running {self.filter_name}...")
        scores = self.scorer.eval(dataframe, input_key)
        dataframe[self.output_key] = scores
        filtered_dataframe = dataframe[(scores >= self.min_score) & (scores <= self.max_score)]
        storage.write(filtered_dataframe)
        self.logger.info(f"Filtering completed. Total records passing filter: {len(filtered_dataframe)}.")
        return [self.output_key]
