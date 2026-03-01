# QUICK START GUIDE
## Softball Pitching Biomechanics Analyzer

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Analyze Your Video
```bash
python softball_analyzer.py your_pitch_video.mp4
```

### Step 3: View Results
Check the `output/` folder for:
- **analyzed_your_pitch_video.mp4** - Video with skeleton tracking
- **biomechanics_*.csv** - All the data
- **report_*.txt** - Analysis report
- **summary_*.json** - Statistical summary

---

## 📊 Generate Visualizations
```bash
python visualize.py output/biomechanics_*.csv
```
Creates charts in `output/plots/`

---

## 📹 Video Recording Tips

**For Best Results:**
1. **Frame Rate**: 240 FPS (use phone slow-motion mode)
2. **Position**: Side view, perpendicular to pitching motion
3. **Distance**: 15-20 feet away
4. **Lighting**: Bright and even
5. **Background**: Contrasting (dark clothes on light background)
6. **Stability**: Use tripod - NO camera movement!

---

## 🎯 Key Metrics to Watch

| Metric | Safe Range | Why It Matters |
|--------|-----------|----------------|
| Elbow Angle | 90-150° | <90° = injury risk ⚠️ |
| Hip-Shoulder Sep | 30-55° | Power generation |
| Stride Length | 75-85% | Efficiency & safety |
| Trunk Lean | 20-40° | Reduces shoulder stress |

---

## 🔧 Common Issues

**"Could not open video"**
- Convert to MP4: `ffmpeg -i input.mov -c:v libx264 output.mp4`

**Poor tracking**
- Improve lighting
- Ensure high contrast
- Use higher resolution (1080p+)

**Left-handed pitcher**
```bash
python softball_analyzer.py video.mp4 left
```

---

## 📚 More Examples

See `examples.py` for:
- Batch processing multiple videos
- Custom data analysis
- Session comparisons
- Injury risk screening

---

## 🆘 Need Help?

1. Read full README.md
2. Check examples.py for code samples
3. Verify video meets recommendations
4. Test with a short clip first

---

**You're ready to go! Record a pitch and run the analyzer!** 🥎

