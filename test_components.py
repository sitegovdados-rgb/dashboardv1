"""
Testes unitários para componentes e utilitários
"""
import unittest
import pandas as pd
from pathlib import Path
from logger_config import DashboardLogger
from cache_manager import CacheManager
from themes import ThemeManager, THEMES


class TestDashboardLogger(unittest.TestCase):
    """Testes para o sistema de logging"""
    
    def setUp(self):
        """Setup para testes"""
        self.logger = DashboardLogger("test_logs")
    
    def test_log_creation(self):
        """Testa criação do logger"""
        self.assertIsNotNone(self.logger)
        self.assertTrue(Path("test_logs").exists())
    
    def test_event_logging(self):
        """Testa logging de eventos"""
        self.logger.log_event(
            "test_event",
            {"test_key": "test_value"}
        )
        self.assertTrue(self.logger.events_log.exists())
    
    def test_file_upload_logging(self):
        """Testa logging de upload"""
        self.logger.log_file_upload("test.csv", 1024)
        stats = self.logger.get_stats()
        self.assertEqual(stats["uploads"], 1)
    
    def test_download_logging(self):
        """Testa logging de download"""
        self.logger.log_download("test.csv", 100)
        stats = self.logger.get_stats()
        self.assertEqual(stats["downloads"], 1)
    
    def test_error_logging(self):
        """Testa logging de erros"""
        self.logger.log_error("Test error", {"context": "test"})
        stats = self.logger.get_stats()
        self.assertEqual(stats["errors"], 1)


class TestCacheManager(unittest.TestCase):
    """Testes para o gerenciador de cache"""
    
    def setUp(self):
        """Setup para testes"""
        self.cache = CacheManager()
        self.test_df = pd.DataFrame({
            'Região': ['A', 'B', 'A'],
            'Status_Execução': ['Em execução', 'Concluída', 'Bloqueada'],
            'Tipo_Atividade': ['Contínua', 'Temporária', 'Esporádica']
        })
    
    def test_calculate_statistics(self):
        """Testa cálculo de estatísticas"""
        stats = self.cache.calculate_statistics(self.test_df)
        
        self.assertEqual(stats['total_rows'], 3)
        self.assertEqual(stats['total_columns'], 3)
        self.assertGreaterEqual(stats['memory_usage'], 0)
    
    def test_get_unique_values(self):
        """Testa obtenção de valores únicos"""
        unique_regions = self.cache.get_unique_values(self.test_df, 'Região')
        self.assertEqual(len(unique_regions), 2)
        self.assertIn('A', unique_regions)
        self.assertIn('B', unique_regions)
    
    def test_filter_dataframe(self):
        """Testa filtragem de DataFrame"""
        filtered = self.cache.filter_dataframe(
            self.test_df,
            region_filter=['A']
        )
        self.assertEqual(len(filtered), 2)


class TestThemeManager(unittest.TestCase):
    """Testes para o gerenciador de temas"""
    
    def test_theme_exists(self):
        """Testa existência de temas"""
        for theme_name in ['light', 'dark', 'blue', 'green']:
            self.assertIn(theme_name, THEMES)
    
    def test_theme_has_required_fields(self):
        """Testa se temas têm campos obrigatórios"""
        required_fields = [
            'primaryColor',
            'backgroundColor',
            'secondaryBackgroundColor',
            'textColor',
            'name',
            'chart_template'
        ]
        
        for theme in THEMES.values():
            for field in required_fields:
                self.assertIn(field, theme)
    
    def test_get_chart_template(self):
        """Testa obtenção de template de gráfico"""
        template = ThemeManager.get_chart_template('dark')
        self.assertEqual(template, 'plotly_dark')
        
        template = ThemeManager.get_chart_template('light')
        self.assertEqual(template, 'plotly')
    
    def test_get_theme_colors(self):
        """Testa obtenção de cores do tema"""
        colors = ThemeManager.get_theme_colors('light')
        self.assertIsNotNone(colors['primaryColor'])
        self.assertIsNotNone(colors['backgroundColor'])


class TestDataProcessing(unittest.TestCase):
    """Testes para processamento de dados"""
    
    def setUp(self):
        """Setup para testes"""
        self.test_data = pd.DataFrame({
            'Tarefa': ['Initiative 1', 'Initiative 2', 'Initiative 3'],
            'Região (PCI)': ['North', 'South', 'North'],
            'Status': ['Em execução', 'Concluída', 'Bloqueada'],
            'Tipo': ['Contínua', 'Temporária', 'Esporádica']
        })
    
    def test_column_mapping(self):
        """Testa mapeamento de colunas"""
        colmap = {
            'Tarefa': 'Iniciativa',
            'Região (PCI)': 'Região',
            'Status': 'Status_Execução',
            'Tipo': 'Tipo_Atividade'
        }
        
        df_mapped = self.test_data.copy()
        df_mapped.columns = [
            colmap.get(col, col) for col in df_mapped.columns
        ]
        
        self.assertIn('Iniciativa', df_mapped.columns)
        self.assertIn('Região', df_mapped.columns)
        self.assertNotIn('Tarefa', df_mapped.columns)
    
    def test_null_values(self):
        """Testa detecção de valores nulos"""
        df_with_nulls = self.test_data.copy()
        df_with_nulls.loc[0, 'Tarefa'] = None
        
        null_count = df_with_nulls.isnull().sum().sum()
        self.assertEqual(null_count, 1)


if __name__ == '__main__':
    unittest.main()
