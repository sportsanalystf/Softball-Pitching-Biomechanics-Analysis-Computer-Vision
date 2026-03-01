"""
Example usage scripts for Softball Pitching Biomechanics Analyzer
"""

from softball_analyzer import SoftballPitchingAnalyzer
from visualize import BiomechanicsVisualizer
from pathlib import Path


def example_1_basic_analysis():
    """
    Example 1: Basic single video analysis
    """
    print("="*60)
    print("EXAMPLE 1: Basic Analysis")
    print("="*60)
    
    # Replace with your video path
    video_path = "pitch_video.mp4"
    
    # Create analyzer
    analyzer = SoftballPitchingAnalyzer(video_path, output_dir="output/example1")
    
    # Process video (right-handed pitcher)
    analyzer.process_video(throwing_arm='right', save_video=True)
    
    # Export data
    df, summary = analyzer.export_data()
    
    # Generate report
    analyzer.generate_report(df)
    
    print("\n✓ Example 1 complete! Check output/example1/")


def example_2_left_handed():
    """
    Example 2: Left-handed pitcher analysis
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Left-Handed Pitcher")
    print("="*60)
    
    video_path = "lefty_pitch.mp4"
    
    analyzer = SoftballPitchingAnalyzer(video_path, output_dir="output/example2")
    
    # Specify left-handed throwing arm
    analyzer.process_video(throwing_arm='left', save_video=True)
    
    df, summary = analyzer.export_data()
    analyzer.generate_report(df)
    
    print("\n✓ Example 2 complete!")


def example_3_custom_analysis():
    """
    Example 3: Custom analysis with data exploration
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Custom Data Analysis")
    print("="*60)
    
    video_path = "pitch_video.mp4"
    
    analyzer = SoftballPitchingAnalyzer(video_path, output_dir="output/example3")
    analyzer.process_video(throwing_arm='right', save_video=False)  # Skip video save
    
    df, summary = analyzer.export_data()
    
    # Custom analysis
    print("\nCustom Analysis:")
    print(f"Total frames analyzed: {len(df)}")
    print(f"Average elbow angle: {df['elbow_angle'].mean():.1f}°")
    print(f"Peak elbow angle: {df['elbow_angle'].max():.1f}°")
    print(f"Average hip-shoulder separation: {df['hip_shoulder_separation'].mean():.1f}°")
    
    # Find critical moments
    max_separation_frame = df.loc[df['hip_shoulder_separation'].idxmax()]
    print(f"\nMax hip-shoulder separation occurred at:")
    print(f"  Frame: {max_separation_frame['frame']}")
    print(f"  Time: {max_separation_frame['time_sec']:.2f}s")
    print(f"  Phase: {max_separation_frame['phase']}")
    print(f"  Separation: {max_separation_frame['hip_shoulder_separation']:.1f}°")
    
    # Injury risk check
    risky_frames = df[df['elbow_angle'] < 90]
    if len(risky_frames) > 0:
        print(f"\n⚠ Warning: {len(risky_frames)} frames with elbow angle < 90° (injury risk)")
    else:
        print("\n✓ Elbow angles within safe range throughout pitch")
    
    print("\n✓ Example 3 complete!")


def example_4_batch_processing():
    """
    Example 4: Process multiple videos in a folder
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Batch Processing Multiple Videos")
    print("="*60)
    
    # Create example video folder structure
    video_folder = Path("videos")
    
    if not video_folder.exists():
        print(f"Create a 'videos' folder and add your .mp4 files")
        return
    
    video_files = list(video_folder.glob("*.mp4"))
    
    if not video_files:
        print("No video files found in 'videos' folder")
        return
    
    print(f"Found {len(video_files)} videos to process\n")
    
    results = []
    
    for idx, video_file in enumerate(video_files, 1):
        print(f"\n[{idx}/{len(video_files)}] Processing {video_file.name}...")
        
        try:
            # Create separate output folder for each video
            output_dir = f"output/batch/{video_file.stem}"
            
            analyzer = SoftballPitchingAnalyzer(video_file, output_dir=output_dir)
            analyzer.process_video(throwing_arm='right', save_video=True)
            df, summary = analyzer.export_data()
            
            # Store key metrics
            results.append({
                'video': video_file.name,
                'avg_elbow': df['elbow_angle'].mean(),
                'avg_separation': df['hip_shoulder_separation'].mean(),
                'avg_stride': df['stride_length_pct'].mean()
            })
            
            print(f"✓ {video_file.name} complete")
            
        except Exception as e:
            print(f"✗ Error processing {video_file.name}: {e}")
    
    # Summary comparison
    print("\n" + "="*60)
    print("BATCH PROCESSING SUMMARY")
    print("="*60)
    print(f"\n{'Video':<30} {'Elbow°':<10} {'Hip-Shoulder°':<15} {'Stride%':<10}")
    print("-" * 65)
    
    for result in results:
        print(f"{result['video']:<30} {result['avg_elbow']:<10.1f} "
              f"{result['avg_separation']:<15.1f} {result['avg_stride']:<10.1f}")
    
    print("\n✓ Batch processing complete!")


def example_5_visualization():
    """
    Example 5: Generate all visualizations from existing data
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: Creating Visualizations")
    print("="*60)
    
    # Find most recent CSV file
    output_dir = Path("output")
    csv_files = list(output_dir.glob("**/biomechanics_*.csv"))
    
    if not csv_files:
        print("No data files found. Run analysis first (Examples 1-3)")
        return
    
    # Use most recent file
    latest_csv = max(csv_files, key=lambda p: p.stat().st_mtime)
    print(f"Using data file: {latest_csv}")
    
    # Create visualizer
    viz = BiomechanicsVisualizer(latest_csv)
    
    # Generate all plots
    viz.create_all_plots(output_dir='output/visualizations')
    
    print("\n✓ Visualizations created in output/visualizations/")


def example_6_session_comparison():
    """
    Example 6: Compare two training sessions
    """
    print("\n" + "="*60)
    print("EXAMPLE 6: Session Comparison")
    print("="*60)
    
    # You need two CSV files from different sessions
    session1_csv = "output/session1/biomechanics_20241122_100000.csv"
    session2_csv = "output/session2/biomechanics_20241122_140000.csv"
    
    if not Path(session1_csv).exists() or not Path(session2_csv).exists():
        print("Need two session CSV files for comparison")
        print("Run analysis on two different videos first")
        return
    
    viz = BiomechanicsVisualizer(session1_csv)
    viz.plot_comparison(session2_csv, save_path='output/session_comparison.png')
    
    print("\n✓ Comparison plot saved to output/session_comparison.png")


def example_7_injury_screening():
    """
    Example 7: Automated injury risk screening
    """
    print("\n" + "="*60)
    print("EXAMPLE 7: Injury Risk Screening")
    print("="*60)
    
    video_path = "pitch_video.mp4"
    
    analyzer = SoftballPitchingAnalyzer(video_path, output_dir="output/screening")
    analyzer.process_video(throwing_arm='right', save_video=False)
    df, summary = analyzer.export_data()
    
    print("\nINJURY RISK ASSESSMENT")
    print("-" * 40)
    
    risk_factors = []
    
    # Check elbow angle
    avg_elbow = df['elbow_angle'].mean()
    min_elbow = df['elbow_angle'].min()
    
    if avg_elbow < 90 or min_elbow < 80:
        risk_factors.append("⚠ HIGH RISK: Low elbow angles detected")
        print(f"⚠ Elbow angle: {avg_elbow:.1f}° (avg), {min_elbow:.1f}° (min)")
        print(f"   Risk: Increased shoulder distraction force")
    else:
        print(f"✓ Elbow angle: {avg_elbow:.1f}° - SAFE")
    
    # Check hip-shoulder separation
    avg_separation = df['hip_shoulder_separation'].mean()
    
    if avg_separation < 30:
        risk_factors.append("⚠ MODERATE RISK: Limited hip-shoulder separation")
        print(f"⚠ Hip-shoulder separation: {avg_separation:.1f}°")
        print(f"   Risk: Increased arm stress, reduced power")
    else:
        print(f"✓ Hip-shoulder separation: {avg_separation:.1f}° - GOOD")
    
    # Check stride length
    avg_stride = df['stride_length_pct'].mean()
    
    if avg_stride > 90:
        risk_factors.append("⚠ MODERATE RISK: Excessive stride length")
        print(f"⚠ Stride length: {avg_stride:.1f}% of height")
        print(f"   Risk: Increased shoulder stress")
    elif avg_stride < 70:
        print(f"⚠ Stride length: {avg_stride:.1f}% (short)")
        print(f"   Note: May limit velocity generation")
    else:
        print(f"✓ Stride length: {avg_stride:.1f}% - OPTIMAL")
    
    # Overall assessment
    print("\n" + "="*40)
    if not risk_factors:
        print("✓ OVERALL: Low injury risk - mechanics within normal ranges")
    else:
        print(f"⚠ OVERALL: {len(risk_factors)} risk factor(s) identified:")
        for factor in risk_factors:
            print(f"  • {factor}")
        print("\n  Recommendation: Consider mechanical coaching intervention")
    
    print("\n✓ Screening complete!")


def main():
    """
    Run examples (comment/uncomment as needed)
    """
    print("\n" + "="*60)
    print("SOFTBALL PITCHING ANALYZER - EXAMPLES")
    print("="*60)
    print("\nThese examples demonstrate different use cases.")
    print("Edit this file to uncomment the examples you want to run.\n")
    
    # Uncomment the examples you want to run:
    
    # example_1_basic_analysis()
    # example_2_left_handed()
    # example_3_custom_analysis()
    # example_4_batch_processing()
    # example_5_visualization()
    # example_6_session_comparison()
    # example_7_injury_screening()
    
    print("\n" + "="*60)
    print("To run examples:")
    print("1. Edit examples.py")
    print("2. Uncomment the example(s) you want")
    print("3. Update video paths to match your files")
    print("4. Run: python examples.py")
    print("="*60)


if __name__ == "__main__":
    main()
