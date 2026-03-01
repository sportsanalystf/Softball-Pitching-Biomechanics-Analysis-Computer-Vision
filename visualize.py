"""
Visualization tools for softball pitching biomechanics data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from pathlib import Path


class BiomechanicsVisualizer:
    def __init__(self, data_path):
        """
        Initialize visualizer with data CSV
        
        Args:
            data_path: Path to CSV file from SoftballPitchingAnalyzer
        """
        self.data = pd.read_csv(data_path)
        self.data_path = Path(data_path)
        
    def plot_angle_timeseries(self, save_path=None):
        """
        Plot key angles over time with phase markers
        """
        fig, axes = plt.subplots(3, 2, figsize=(15, 12))
        fig.suptitle('Biomechanical Angles Throughout Pitch', fontsize=16, fontweight='bold')
        
        angles = [
            ('elbow_angle', 'Elbow Angle', (90, 150), '°'),
            ('hip_shoulder_separation', 'Hip-Shoulder Separation', (30, 55), '°'),
            ('stride_knee_angle', 'Stride Knee Angle', (140, 180), '°'),
            ('drive_knee_angle', 'Drive Knee Angle', (120, 180), '°'),
            ('trunk_lean', 'Trunk Forward Lean', (20, 40), '°'),
            ('stride_length_pct', 'Stride Length', (75, 85), '% height')
        ]
        
        for idx, (col, title, (min_opt, max_opt), unit) in enumerate(angles):
            ax = axes[idx // 2, idx % 2]
            
            if col in self.data.columns:
                # Plot the angle
                ax.plot(self.data['time_sec'], self.data[col], 
                       linewidth=2, color='#2E86AB', label='Measured')
                
                # Add optimal range
                ax.axhspan(min_opt, max_opt, alpha=0.2, color='green', 
                          label='Optimal Range')
                
                # Mark phases with vertical lines
                if 'phase' in self.data.columns:
                    phase_changes = self.data[self.data['phase'] != self.data['phase'].shift()]
                    for _, row in phase_changes.iterrows():
                        ax.axvline(row['time_sec'], color='red', 
                                 linestyle='--', alpha=0.5)
                
                ax.set_xlabel('Time (seconds)', fontsize=10)
                ax.set_ylabel(f'{title} ({unit})', fontsize=10)
                ax.set_title(title, fontsize=12, fontweight='bold')
                ax.grid(True, alpha=0.3)
                ax.legend(loc='best', fontsize=8)
            else:
                ax.text(0.5, 0.5, f'No data for {title}', 
                       ha='center', va='center', transform=ax.transAxes)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved plot: {save_path}")
        else:
            plt.show()
        
        return fig
    
    def plot_phase_breakdown(self, save_path=None):
        """
        Plot average angles for each pitch phase
        """
        if 'phase' not in self.data.columns:
            print("No phase data available")
            return
        
        metrics = ['elbow_angle', 'hip_shoulder_separation', 'stride_knee_angle', 
                  'trunk_lean', 'stride_length_pct']
        
        # Filter to available metrics
        available_metrics = [m for m in metrics if m in self.data.columns]
        
        if not available_metrics:
            print("No metrics available for phase breakdown")
            return
        
        # Calculate mean by phase
        phase_means = self.data.groupby('phase')[available_metrics].mean()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(phase_means.index))
        width = 0.15
        
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']
        
        for idx, metric in enumerate(available_metrics):
            offset = width * (idx - len(available_metrics)/2)
            bars = ax.bar(x + offset, phase_means[metric], width, 
                         label=metric.replace('_', ' ').title(),
                         color=colors[idx % len(colors)])
        
        ax.set_xlabel('Pitch Phase', fontsize=12, fontweight='bold')
        ax.set_ylabel('Angle (degrees or %)', fontsize=12, fontweight='bold')
        ax.set_title('Biomechanical Metrics by Pitch Phase', 
                    fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(phase_means.index, rotation=15, ha='right')
        ax.legend(loc='best')
        ax.grid(True, axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved plot: {save_path}")
        else:
            plt.show()
        
        return fig
    
    def plot_summary_dashboard(self, save_path=None):
        """
        Create a comprehensive dashboard with multiple visualizations
        """
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Title
        fig.suptitle('Softball Pitching Biomechanics Dashboard', 
                    fontsize=18, fontweight='bold', y=0.98)
        
        # 1. Elbow angle over time (large)
        ax1 = fig.add_subplot(gs[0, :2])
        if 'elbow_angle' in self.data.columns:
            ax1.plot(self.data['time_sec'], self.data['elbow_angle'], 
                    linewidth=2, color='#2E86AB')
            ax1.axhspan(90, 150, alpha=0.2, color='green', label='Safe Zone')
            ax1.set_title('Elbow Angle (Injury Risk Indicator)', fontweight='bold')
            ax1.set_xlabel('Time (sec)')
            ax1.set_ylabel('Angle (°)')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
        
        # 2. Phase distribution (pie)
        ax2 = fig.add_subplot(gs[0, 2])
        if 'phase' in self.data.columns:
            phase_counts = self.data['phase'].value_counts()
            colors_pie = plt.cm.Set3(range(len(phase_counts)))
            ax2.pie(phase_counts.values, labels=phase_counts.index, autopct='%1.1f%%',
                   colors=colors_pie, startangle=90)
            ax2.set_title('Pitch Phase Distribution', fontweight='bold')
        
        # 3. Hip-shoulder separation
        ax3 = fig.add_subplot(gs[1, 0])
        if 'hip_shoulder_separation' in self.data.columns:
            ax3.plot(self.data['time_sec'], self.data['hip_shoulder_separation'],
                    linewidth=2, color='#A23B72')
            ax3.axhspan(30, 55, alpha=0.2, color='green')
            ax3.set_title('Hip-Shoulder Separation', fontweight='bold')
            ax3.set_xlabel('Time (sec)')
            ax3.set_ylabel('Separation (°)')
            ax3.grid(True, alpha=0.3)
        
        # 4. Stride length
        ax4 = fig.add_subplot(gs[1, 1])
        if 'stride_length_pct' in self.data.columns:
            ax4.plot(self.data['time_sec'], self.data['stride_length_pct'],
                    linewidth=2, color='#F18F01')
            ax4.axhspan(75, 85, alpha=0.2, color='green')
            ax4.set_title('Stride Length', fontweight='bold')
            ax4.set_xlabel('Time (sec)')
            ax4.set_ylabel('% of Height')
            ax4.grid(True, alpha=0.3)
        
        # 5. Trunk lean
        ax5 = fig.add_subplot(gs[1, 2])
        if 'trunk_lean' in self.data.columns:
            ax5.plot(self.data['time_sec'], self.data['trunk_lean'],
                    linewidth=2, color='#6A994E')
            ax5.axhspan(20, 40, alpha=0.2, color='green')
            ax5.set_title('Trunk Forward Lean', fontweight='bold')
            ax5.set_xlabel('Time (sec)')
            ax5.set_ylabel('Angle (°)')
            ax5.grid(True, alpha=0.3)
        
        # 6. Summary statistics table
        ax6 = fig.add_subplot(gs[2, :])
        ax6.axis('off')
        
        # Create summary table
        metrics_summary = []
        metric_names = [
            ('elbow_angle', 'Elbow Angle', (90, 150)),
            ('hip_shoulder_separation', 'Hip-Shoulder Sep', (30, 55)),
            ('stride_length_pct', 'Stride Length', (75, 85)),
            ('trunk_lean', 'Trunk Lean', (20, 40))
        ]
        
        for col, name, (min_opt, max_opt) in metric_names:
            if col in self.data.columns:
                mean_val = self.data[col].mean()
                std_val = self.data[col].std()
                status = '✓' if min_opt <= mean_val <= max_opt else '⚠'
                metrics_summary.append([
                    name,
                    f'{mean_val:.1f} ± {std_val:.1f}',
                    f'{min_opt}-{max_opt}',
                    status
                ])
        
        if metrics_summary:
            table = ax6.table(cellText=metrics_summary,
                            colLabels=['Metric', 'Mean ± Std', 'Optimal Range', 'Status'],
                            cellLoc='center',
                            loc='center',
                            bbox=[0.1, 0, 0.8, 1])
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 2)
            
            # Color code status column
            for i in range(len(metrics_summary)):
                cell = table[(i+1, 3)]
                if metrics_summary[i][3] == '✓':
                    cell.set_facecolor('#90EE90')
                else:
                    cell.set_facecolor('#FFB6C1')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved dashboard: {save_path}")
        else:
            plt.show()
        
        return fig
    
    def plot_comparison(self, other_data_path, save_path=None):
        """
        Compare two pitching sessions
        
        Args:
            other_data_path: Path to second CSV for comparison
        """
        other_data = pd.read_csv(other_data_path)
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Pitching Session Comparison', fontsize=16, fontweight='bold')
        
        metrics = ['elbow_angle', 'hip_shoulder_separation', 
                  'stride_length_pct', 'trunk_lean']
        titles = ['Elbow Angle', 'Hip-Shoulder Separation', 
                 'Stride Length', 'Trunk Lean']
        
        for idx, (metric, title) in enumerate(zip(metrics, titles)):
            ax = axes[idx // 2, idx % 2]
            
            if metric in self.data.columns and metric in other_data.columns:
                # Plot both datasets
                ax.plot(self.data['time_sec'], self.data[metric], 
                       linewidth=2, label='Session 1', color='#2E86AB')
                ax.plot(other_data['time_sec'], other_data[metric], 
                       linewidth=2, label='Session 2', color='#A23B72', 
                       linestyle='--')
                
                ax.set_title(title, fontweight='bold')
                ax.set_xlabel('Time (sec)')
                ax.set_ylabel(metric.replace('_', ' ').title())
                ax.grid(True, alpha=0.3)
                ax.legend()
            else:
                ax.text(0.5, 0.5, f'Data not available', 
                       ha='center', va='center', transform=ax.transAxes)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved comparison: {save_path}")
        else:
            plt.show()
        
        return fig
    
    def create_all_plots(self, output_dir='output/plots'):
        """
        Generate all available plots
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print("Generating visualizations...")
        
        # Time series
        self.plot_angle_timeseries(
            save_path=output_path / 'angle_timeseries.png'
        )
        
        # Phase breakdown
        self.plot_phase_breakdown(
            save_path=output_path / 'phase_breakdown.png'
        )
        
        # Dashboard
        self.plot_summary_dashboard(
            save_path=output_path / 'dashboard.png'
        )
        
        print(f"\n✓ All plots saved to: {output_path}")


def main():
    """
    Example usage for visualization
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python visualize.py <csv_data_path>")
        print("Example: python visualize.py output/biomechanics_20241122_143022.csv")
        sys.exit(1)
    
    data_path = sys.argv[1]
    
    visualizer = BiomechanicsVisualizer(data_path)
    visualizer.create_all_plots()
    
    print("\n✓ Visualization complete!")


if __name__ == "__main__":
    main()
