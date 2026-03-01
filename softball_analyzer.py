"""
Softball Pitching Biomechanics Analyzer
Uses MediaPipe Pose for keypoint detection and biomechanical analysis
"""

import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
from pathlib import Path
import json
from datetime import datetime


class SoftballPitchingAnalyzer:
    def __init__(self, video_path, output_dir="output"):
        """
        Initialize the softball pitching analyzer
        
        Args:
            video_path: Path to video file
            output_dir: Directory for output files
        """
        self.video_path = video_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=1  # 0=lite, 1=full (locally available), 2=heavy
        )
        
        # Storage for analysis data
        self.frame_data = []
        self.biomechanics_summary = {}
        
    def calculate_angle(self, a, b, c):
        """
        Calculate angle at point b formed by points a-b-c
        
        Args:
            a, b, c: Points as (x, y, z) tuples or arrays
            
        Returns:
            Angle in degrees
        """
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        ba = a - b
        bc = c - b
        
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
        angle = np.arccos(cosine_angle)
        
        return np.degrees(angle)
    
    def calculate_2d_angle(self, a, b, c):
        """
        Calculate angle in 2D plane (ignoring z-coordinate)
        Useful for hip-shoulder separation
        """
        # Use only x, y coordinates
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - \
                  np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(np.degrees(radians))
        
        # Normalize to 0-180 range
        if angle > 180:
            angle = 360 - angle
            
        return angle
    
    def extract_keypoints(self, landmarks, frame_shape):
        """
        Extract key body landmarks for biomechanical analysis
        
        Returns:
            Dictionary of keypoint coordinates (x, y, z, visibility)
        """
        h, w = frame_shape[:2]
        
        keypoints = {}
        landmark_names = {
            'nose': self.mp_pose.PoseLandmark.NOSE,
            'left_shoulder': self.mp_pose.PoseLandmark.LEFT_SHOULDER,
            'right_shoulder': self.mp_pose.PoseLandmark.RIGHT_SHOULDER,
            'left_elbow': self.mp_pose.PoseLandmark.LEFT_ELBOW,
            'right_elbow': self.mp_pose.PoseLandmark.RIGHT_ELBOW,
            'left_wrist': self.mp_pose.PoseLandmark.LEFT_WRIST,
            'right_wrist': self.mp_pose.PoseLandmark.RIGHT_WRIST,
            'left_hip': self.mp_pose.PoseLandmark.LEFT_HIP,
            'right_hip': self.mp_pose.PoseLandmark.RIGHT_HIP,
            'left_knee': self.mp_pose.PoseLandmark.LEFT_KNEE,
            'right_knee': self.mp_pose.PoseLandmark.RIGHT_KNEE,
            'left_ankle': self.mp_pose.PoseLandmark.LEFT_ANKLE,
            'right_ankle': self.mp_pose.PoseLandmark.RIGHT_ANKLE,
        }
        
        for name, landmark_id in landmark_names.items():
            lm = landmarks.landmark[landmark_id]
            keypoints[name] = {
                'x': lm.x * w,
                'y': lm.y * h,
                'z': lm.z * w,  # Relative depth
                'visibility': lm.visibility
            }
        
        return keypoints
    
    def calculate_biomechanics(self, keypoints, throwing_arm='right'):
        """
        Calculate key biomechanical measurements
        
        Args:
            keypoints: Dictionary of body landmarks
            throwing_arm: 'right' or 'left'
            
        Returns:
            Dictionary of biomechanical metrics
        """
        metrics = {}
        
        # Determine arm side
        arm_prefix = throwing_arm
        opposite_prefix = 'left' if throwing_arm == 'right' else 'right'
        
        # Extract coordinates
        def get_coords(name):
            kp = keypoints[name]
            return np.array([kp['x'], kp['y'], kp['z']])
        
        # 1. ELBOW ANGLE (critical for injury risk)
        shoulder = get_coords(f'{arm_prefix}_shoulder')
        elbow = get_coords(f'{arm_prefix}_elbow')
        wrist = get_coords(f'{arm_prefix}_wrist')
        metrics['elbow_angle'] = self.calculate_angle(shoulder, elbow, wrist)
        
        # 2. KNEE ANGLES (both legs)
        # Stride leg (opposite to throwing arm)
        stride_hip = get_coords(f'{opposite_prefix}_hip')
        stride_knee = get_coords(f'{opposite_prefix}_knee')
        stride_ankle = get_coords(f'{opposite_prefix}_ankle')
        metrics['stride_knee_angle'] = self.calculate_angle(stride_hip, stride_knee, stride_ankle)
        
        # Drive leg
        drive_hip = get_coords(f'{arm_prefix}_hip')
        drive_knee = get_coords(f'{arm_prefix}_knee')
        drive_ankle = get_coords(f'{arm_prefix}_ankle')
        metrics['drive_knee_angle'] = self.calculate_angle(drive_hip, drive_knee, drive_ankle)
        
        # 3. TRUNK FLEXION (forward lean)
        left_shoulder = get_coords('left_shoulder')
        right_shoulder = get_coords('right_shoulder')
        left_hip = get_coords('left_hip')
        right_hip = get_coords('right_hip')
        
        shoulder_center = (left_shoulder + right_shoulder) / 2
        hip_center = (left_hip + right_hip) / 2
        
        # Calculate trunk angle relative to vertical
        trunk_vector = shoulder_center - hip_center
        vertical_vector = np.array([0, -1, 0])  # Pointing up
        metrics['trunk_lean'] = self.calculate_angle(
            shoulder_center + vertical_vector,
            shoulder_center,
            hip_center
        )
        
        # 4. HIP-SHOULDER SEPARATION (rotational)
        # Calculate angles of hip line and shoulder line in 2D
        hip_angle = np.arctan2(
            right_hip[1] - left_hip[1],
            right_hip[0] - left_hip[0]
        )
        shoulder_angle = np.arctan2(
            right_shoulder[1] - left_shoulder[1],
            right_shoulder[0] - left_shoulder[0]
        )
        
        separation = np.abs(np.degrees(hip_angle - shoulder_angle))
        if separation > 180:
            separation = 360 - separation
        metrics['hip_shoulder_separation'] = separation
        
        # 5. STRIDE LENGTH (distance between ankles, normalized by height estimate)
        stride_length_pixels = np.linalg.norm(stride_ankle[:2] - drive_ankle[:2])
        
        # Estimate height from hip to nose
        nose = get_coords('nose')
        estimated_height = np.linalg.norm(nose[:2] - hip_center[:2])
        
        # Stride as percentage of height (typically 75-85%)
        metrics['stride_length_pct'] = (stride_length_pixels / estimated_height) * 100 if estimated_height > 0 else 0
        
        # 6. SHOULDER ANGLE (arm slot)
        metrics['shoulder_angle'] = self.calculate_angle(
            elbow,
            shoulder,
            hip_center
        )
        
        # Add visibility scores for quality control
        metrics['avg_visibility'] = np.mean([
            keypoints[f'{arm_prefix}_wrist']['visibility'],
            keypoints[f'{arm_prefix}_elbow']['visibility'],
            keypoints[f'{arm_prefix}_shoulder']['visibility']
        ])
        
        return metrics
    
    def detect_pitch_phase(self, metrics, frame_idx):
        """
        Simple pitch phase detection based on biomechanics
        More sophisticated version would use ML classifier
        
        Returns:
            Phase name: 'wind_up', 'stride', 'acceleration', 'release', 'follow_through'
        """
        # This is a simplified heuristic approach
        # Professional systems use trained classifiers
        
        stride_knee = metrics['stride_knee_angle']
        elbow = metrics['elbow_angle']
        
        if stride_knee > 160:  # Leg relatively straight
            if elbow < 100:
                return 'follow_through'
            elif elbow > 140:
                return 'wind_up'
            else:
                return 'release'
        else:  # Knee bent, stride phase or acceleration
            if elbow > 130:
                return 'stride'
            else:
                return 'acceleration'
    
    def process_video(self, throwing_arm='right', save_video=True):
        """
        Process entire video and extract biomechanics
        
        Args:
            throwing_arm: 'right' or 'left'
            save_video: Save annotated video with skeleton overlay
        """
        cap = cv2.VideoCapture(str(self.video_path))
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {self.video_path}")
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"Processing video: {self.video_path}")
        print(f"Resolution: {frame_width}x{frame_height}, FPS: {fps}, Frames: {total_frames}")
        
        # Setup video writer if saving
        out = None
        if save_video:
            output_path = self.output_dir / f"analyzed_{Path(self.video_path).name}"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (frame_width, frame_height))
        
        frame_idx = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert to RGB for MediaPipe
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            
            # Process with MediaPipe
            results = self.pose.process(image)
            
            # Convert back to BGR for OpenCV
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            if results.pose_landmarks:
                # Draw skeleton
                self.mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                    self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
                )
                
                # Extract keypoints
                keypoints = self.extract_keypoints(results.pose_landmarks, frame.shape)
                
                # Calculate biomechanics
                metrics = self.calculate_biomechanics(keypoints, throwing_arm)
                metrics['frame'] = frame_idx
                metrics['time_sec'] = frame_idx / fps
                
                # Detect phase
                phase = self.detect_pitch_phase(metrics, frame_idx)
                metrics['phase'] = phase
                
                # Store data
                self.frame_data.append(metrics)
                
                # Overlay metrics on video
                y_offset = 30
                cv2.putText(image, f"Frame: {frame_idx}", (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                y_offset += 30
                
                cv2.putText(image, f"Phase: {phase}", (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                y_offset += 30
                
                cv2.putText(image, f"Elbow: {metrics['elbow_angle']:.1f}°", (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                y_offset += 30
                
                cv2.putText(image, f"Hip-Shoulder Sep: {metrics['hip_shoulder_separation']:.1f}°",
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                y_offset += 30
                
                cv2.putText(image, f"Stride: {metrics['stride_length_pct']:.1f}%",
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Save frame
            if out:
                out.write(image)
            
            frame_idx += 1
            
            # Progress indicator
            if frame_idx % 30 == 0:
                print(f"Processed {frame_idx}/{total_frames} frames ({100*frame_idx/total_frames:.1f}%)")
        
        # Cleanup
        cap.release()
        if out:
            out.release()
            print(f"\nSaved annotated video: {output_path}")
        
        print(f"\nProcessing complete! Analyzed {len(self.frame_data)} frames")
        
    def export_data(self):
        """
        Export biomechanics data to CSV and JSON
        """
        if not self.frame_data:
            print("No data to export. Run process_video() first.")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(self.frame_data)
        
        # Save CSV
        csv_path = self.output_dir / f"biomechanics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(csv_path, index=False)
        print(f"Saved data to: {csv_path}")
        
        # Calculate summary statistics
        summary = {
            'video_file': str(self.video_path),
            'total_frames': len(self.frame_data),
            'metrics': {}
        }
        
        numeric_columns = ['elbow_angle', 'stride_knee_angle', 'drive_knee_angle',
                          'trunk_lean', 'hip_shoulder_separation', 'stride_length_pct']
        
        for col in numeric_columns:
            if col in df.columns:
                summary['metrics'][col] = {
                    'mean': float(df[col].mean()),
                    'std': float(df[col].std()),
                    'min': float(df[col].min()),
                    'max': float(df[col].max())
                }
        
        # Phase distribution
        if 'phase' in df.columns:
            summary['phase_distribution'] = df['phase'].value_counts().to_dict()
        
        # Save JSON summary
        json_path = self.output_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_path, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"Saved summary to: {json_path}")
        
        return df, summary
    
    def generate_report(self, df=None):
        """
        Generate a readable text report of key findings
        """
        if df is None:
            if not self.frame_data:
                print("No data available. Run process_video() first.")
                return
            df = pd.DataFrame(self.frame_data)
        
        report = []
        report.append("="*60)
        report.append("SOFTBALL PITCHING BIOMECHANICS ANALYSIS REPORT")
        report.append("="*60)
        report.append(f"\nVideo: {self.video_path}")
        report.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"\nTotal Frames Analyzed: {len(df)}")
        
        # Key metrics summary
        report.append("\n" + "="*60)
        report.append("KEY BIOMECHANICAL METRICS")
        report.append("="*60)
        
        metrics = [
            ('Elbow Angle', 'elbow_angle', '°', (90, 150)),
            ('Hip-Shoulder Separation', 'hip_shoulder_separation', '°', (30, 55)),
            ('Stride Length', 'stride_length_pct', '% height', (75, 85)),
            ('Trunk Lean', 'trunk_lean', '°', (20, 40)),
            ('Stride Knee Angle', 'stride_knee_angle', '°', (140, 180))
        ]
        
        for name, col, unit, (min_optimal, max_optimal) in metrics:
            if col in df.columns:
                mean_val = df[col].mean()
                std_val = df[col].std()
                
                # Check if in optimal range
                status = "✓ OPTIMAL" if min_optimal <= mean_val <= max_optimal else "⚠ CHECK"
                
                report.append(f"\n{name}:")
                report.append(f"  Mean: {mean_val:.1f}{unit} ± {std_val:.1f} [{status}]")
                report.append(f"  Range: {df[col].min():.1f} - {df[col].max():.1f}{unit}")
                report.append(f"  Optimal Range: {min_optimal}-{max_optimal}{unit}")
        
        # Phase distribution
        if 'phase' in df.columns:
            report.append("\n" + "="*60)
            report.append("PITCH PHASE DISTRIBUTION")
            report.append("="*60)
            phase_counts = df['phase'].value_counts()
            for phase, count in phase_counts.items():
                pct = 100 * count / len(df)
                report.append(f"  {phase}: {count} frames ({pct:.1f}%)")
        
        # Recommendations
        report.append("\n" + "="*60)
        report.append("RECOMMENDATIONS")
        report.append("="*60)
        
        recommendations = []
        
        if 'elbow_angle' in df.columns:
            if df['elbow_angle'].mean() < 90:
                recommendations.append("⚠ Low elbow angle may increase injury risk")
        
        if 'hip_shoulder_separation' in df.columns:
            if df['hip_shoulder_separation'].mean() < 30:
                recommendations.append("⚠ Limited hip-shoulder separation - work on rotational mechanics")
        
        if 'stride_length_pct' in df.columns:
            stride_pct = df['stride_length_pct'].mean()
            if stride_pct < 70:
                recommendations.append("⚠ Short stride may limit power generation")
            elif stride_pct > 90:
                recommendations.append("⚠ Long stride may increase shoulder stress")
        
        if not recommendations:
            recommendations.append("✓ Mechanics appear within normal ranges")
        
        for rec in recommendations:
            report.append(f"  {rec}")
        
        report.append("\n" + "="*60)
        
        # Print and save report
        report_text = "\n".join(report)
        print(report_text)
        
        report_path = self.output_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_path, 'w') as f:
            f.write(report_text)
        print(f"\nReport saved to: {report_path}")
        
        return report_text


def main():
    """
    Example usage
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python softball_analyzer.py <video_path> [throwing_arm]")
        print("Example: python softball_analyzer.py pitch_video.mp4 right")
        sys.exit(1)
    
    video_path = sys.argv[1]
    throwing_arm = sys.argv[2] if len(sys.argv) > 2 else 'right'
    
    # Create analyzer
    analyzer = SoftballPitchingAnalyzer(video_path)
    
    # Process video
    print("Starting analysis...")
    analyzer.process_video(throwing_arm=throwing_arm, save_video=True)
    
    # Export data
    df, summary = analyzer.export_data()
    
    # Generate report
    analyzer.generate_report(df)
    
    print("\n✓ Analysis complete! Check the 'output' directory for results.")


if __name__ == "__main__":
    main()
