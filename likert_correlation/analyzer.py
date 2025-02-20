"""Core functionality for Likert scale correlation analysis."""
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats


@dataclass
class AnalysisResults:
    """Container for correlation analysis results."""
    kendall_tau: float
    kendall_p: float
    spearman_rho: float
    spearman_p: float
    sample_size: int
    total_ties: int
    recommended_method: str
    recommendation_reason: str
    kendall_interpretation: str
    spearman_interpretation: str


class LikertAnalyzer:
    """Analyzes correlations between Likert scale variables."""

    def __init__(self):
        self.data: Optional[pd.DataFrame] = None
        self.columns: List[str] = []

    def load_data(self, file_path: Union[str, Path]) -> List[str]:
        """Load data from CSV or Excel file.
        
        Args:
            file_path: Path to the data file
            
        Returns:
            List of column names
            
        Raises:
            ValueError: If file format is not supported
        """
        file_path = Path(file_path)
        if file_path.suffix.lower() == '.csv':
            self.data = pd.read_csv(file_path)
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            self.data = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Please use CSV or Excel files.")
            
        self.columns = list(self.data.columns)
        return self.columns

    @staticmethod
    def _interpret_kendall(tau: float) -> str:
        """Interpret Kendall's tau correlation coefficient."""
        if tau == 1:
            return "Perfect agreement"
        elif 0.4 <= abs(tau) < 1:
            return f"Strong {'agreement' if tau > 0 else 'disagreement'}"
        elif 0.1 <= abs(tau) < 0.4:
            return f"Weak {'agreement' if tau > 0 else 'disagreement'}"
        elif -0.1 < tau < 0.1:
            return "No association"
        else:
            return "Perfect disagreement"

    @staticmethod
    def _interpret_spearman(rho: float) -> str:
        """Interpret Spearman's rho correlation coefficient."""
        if rho == 1:
            return "Perfect positive correlation"
        elif 0.5 <= abs(rho) < 1:
            return f"Strong {'positive' if rho > 0 else 'negative'} correlation"
        elif 0.1 <= abs(rho) < 0.5:
            return f"Weak {'positive' if rho > 0 else 'negative'} correlation"
        elif -0.1 < rho < 0.1:
            return "No correlation"
        else:
            return "Perfect negative correlation"

    def analyze(self, col1: str, col2: str) -> AnalysisResults:
        """Perform correlation analysis on two columns.
        
        Args:
            col1: Name of first column
            col2: Name of second column
            
        Returns:
            AnalysisResults object containing correlation statistics and interpretations
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")

        data1 = self.data[col1].dropna()
        data2 = self.data[col2].dropna()
        
        # Calculate correlations
        kendall_tau, kendall_p = stats.kendalltau(data1, data2)
        spearman_rho, spearman_p = stats.spearmanr(data1, data2)
        
        # Count ties
        ties1 = len(data1) - len(data1.unique())
        ties2 = len(data2) - len(data2.unique())
        total_ties = ties1 + ties2
        
        # Determine recommended method
        sample_size = len(data1)
        if sample_size < 30:
            recommended = "Kendall's tau"
            reason = "Small sample size (n < 30)"
        elif total_ties > sample_size * 0.2:  # More than 20% ties
            recommended = "Kendall's tau"
            reason = f"High number of ties ({total_ties} ties in {sample_size} observations)"
        else:
            recommended = "Spearman's rho"
            reason = "Larger sample size with fewer ties"

        return AnalysisResults(
            kendall_tau=kendall_tau,
            kendall_p=kendall_p,
            spearman_rho=spearman_rho,
            spearman_p=spearman_p,
            sample_size=sample_size,
            total_ties=total_ties,
            recommended_method=recommended,
            recommendation_reason=reason,
            kendall_interpretation=self._interpret_kendall(kendall_tau),
            spearman_interpretation=self._interpret_spearman(spearman_rho)
        )

    def create_visualizations(self, col1: str, col2: str) -> go.Figure:
        """Create visualization figures for the correlation analysis."""
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")
        data1 = self.data[col1].dropna()
        data2 = self.data[col2].dropna()
    
        all_values = list(range(int(min(data1.min(), data2.min())), int(max(data1.max(), data2.max())) + 1))
    
        counts1 = data1.value_counts().reindex(all_values, fill_value=0).sort_index()
        counts2 = data2.value_counts().reindex(all_values, fill_value=0).sort_index()
    
        fig = make_subplots(
            rows=4, cols=1,
            subplot_titles=(
                f'Distribution of {col1}',
                f'Distribution of {col2}',
                'Joint Distribution Heatmap',
                'Scatter Plot with Jitter'
            ),
            vertical_spacing=0.1,
            row_heights=[0.2, 0.2, 0.3, 0.3]
        )
    
        fig.add_trace(
            go.Bar(x=counts1.index, y=counts1.values, name=col1),
            row=1, col=1
        )
    
        fig.add_trace(
            go.Bar(x=counts2.index, y=counts2.values, name=col2),
            row=2, col=1
        )
    
        heatmap_data = pd.crosstab(data1, data2)
        for val1 in all_values:
            if val1 not in heatmap_data.index:
                heatmap_data.loc[val1] = 0
        for val2 in all_values:
            if val2 not in heatmap_data.columns:
                heatmap_data[val2] = 0
    
        heatmap_data = heatmap_data.sort_index().sort_index(axis=1)
    
        # Add heatmap trace without a colorbar first
        fig.add_trace(
            go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                colorscale='Blues',
                showscale=False  # Hide the colorbar for this trace
            ),
            row=3, col=1
        )
        
        # Add an empty scatter trace in the heatmap subplot that will hold our colorbar
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(
                    colorscale='Blues',
                    showscale=True,
                    cmin=heatmap_data.values.min(),
                    cmax=heatmap_data.values.max(),
                    colorbar=dict(
                        title='Count',
                        thickness=20,
                        lenmode='fraction',
                        len=0.3,
                        yanchor='middle',
                        y=0.4,
                        outlinewidth=0
                    )
                ),
                showlegend=False
            ),
            row=3, col=1
        )
    
        jitter = np.random.normal(0, 0.1, size=len(data1))
        fig.add_trace(
            go.Scatter(
                x=data1 + jitter,
                y=data2 + jitter,
                mode='markers',
                marker=dict(size=8, opacity=0.6),
                name='Responses'
            ),
            row=4, col=1
        )
    
        fig.update_layout(
            height=1440,
            width=720,
            showlegend=False,
            title_text="Correlation Analysis Visualizations",
            title_x=0.5,
            margin=dict(
                t=50,
                b=50,
                l=80,
                r=90
            ),
            font=dict(size=12)
        )
        for i in range(1, 5):
            fig.update_xaxes(
                row=i, col=1,
                tickmode='array',
                tickvals=all_values,
                ticktext=all_values,
                tickangle=0,
                dtick=1,
                tickfont=dict(size=11)
            )
        fig.update_xaxes(title_text="Score", title_font=dict(size=12), row=1, col=1)
        fig.update_yaxes(title_text="Count", title_font=dict(size=12), row=1, col=1)
        fig.update_xaxes(title_text="Score", title_font=dict(size=12), row=2, col=1)
        fig.update_yaxes(title_text="Count", title_font=dict(size=12), row=2, col=1)
        fig.update_xaxes(title_text=f"{col1} Score", title_font=dict(size=12), row=3, col=1)
        fig.update_yaxes(title_text=f"{col2} Score", title_font=dict(size=12), row=3, col=1)
        fig.update_xaxes(title_text=f"{col1} Score", title_font=dict(size=12), row=4, col=1)
        fig.update_yaxes(title_text=f"{col2} Score", title_font=dict(size=12), row=4, col=1)
        for i in fig['layout']['annotations']:
            i['font'] = dict(size=13)
        return fig