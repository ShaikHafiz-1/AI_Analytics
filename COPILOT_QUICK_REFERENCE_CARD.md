# Copilot Quick Reference Card

## 🚀 Start Testing in 30 Seconds

### 1. Open Dashboard
```
http://localhost:3000
```

### 2. Click "Ask Copilot" Button
- Blue button with ✦ icon
- Top-right area of dashboard

### 3. Copy & Paste First Prompt
```
What is the current planning health?
```

### 4. Press Enter or Click Send
- Wait for response (< 6 seconds)
- Read answer
- Try next prompt

---

## 📋 5-Minute Test Prompts

Copy these one by one:

```
1. What is the current planning health?
2. What is the current forecast?
3. What are the top risks?
4. How many records have changed?
5. What should we do?
```

---

## 🎯 10-Minute Test Prompts

Add these after the 5-minute test:

```
6. Which suppliers are affected?
7. Are there any design changes?
8. Which locations are most affected?
9. Which material groups have the most changes?
10. How does this compare to last period?
```

---

## 🔍 Drill-Down Testing

### Select Location
1. Scroll to "Location + Material View"
2. Click on a location
3. Ask: "Tell me about this location"

### Select Material Group
1. Click on a material group
2. Ask: "What's happening with this material group?"

### Select Supplier
1. Scroll to "Supplier + Design + ROJ"
2. Click on a supplier
3. Ask: "What is this supplier's impact?"

---

## ✅ What to Look For

### Good Response
- ✅ Answers question directly
- ✅ Shows relevant metrics
- ✅ Provides supporting data
- ✅ Suggests follow-up questions
- ✅ Completes in < 6 seconds

### Problem Response
- ❌ Doesn't answer question
- ❌ Missing data
- ❌ Timeout (> 6 seconds)
- ❌ Irrelevant answer

---

## 🐛 Quick Troubleshooting

| Issue | Fix |
|-------|-----|
| Copilot won't open | Refresh page (F5) |
| Spinner stuck | Wait 6 seconds for timeout |
| Same answer repeated | Try different question |
| Data looks wrong | Check if using mock data |
| Backend not responding | Run `func start` |

---

## 📊 Test Categories

| # | Category | Example Prompt |
|---|----------|-----------------|
| 1 | Health | "What is the current planning health?" |
| 2 | Forecast | "What is the current forecast?" |
| 3 | Risk | "What are the top risks?" |
| 4 | Changes | "How many records have changed?" |
| 5 | Suppliers | "Which suppliers are affected?" |
| 6 | Design | "Are there any design changes?" |
| 7 | Location | "Which locations are most affected?" |
| 8 | Material | "Which material groups have changes?" |
| 9 | Actions | "What should we do?" |
| 10 | Comparison | "How does this compare to last period?" |

---

## 🎬 Test Scenarios

### Scenario 1: Executive Review (10 min)
- Health → Forecast → Risk → Actions

### Scenario 2: Supplier Analysis (15 min)
- Suppliers → Select supplier → Drill-down

### Scenario 3: Location Analysis (15 min)
- Locations → Select location → Drill-down

### Scenario 4: Material Analysis (15 min)
- Material groups → Select group → Drill-down

### Scenario 5: Risk Mitigation (15 min)
- Risks → Details → Mitigation → Impact

---

## 📈 Performance Targets

| Metric | Target |
|--------|--------|
| Response Time | < 6 seconds |
| Accuracy | 100% |
| Relevance | 100% |
| Follow-ups | Present |
| Errors | 0 |

---

## 🎯 Success Criteria

✅ **Test Passed If**:
- All responses are relevant
- All responses are accurate
- Response time < 6 seconds
- Follow-up suggestions appear
- Drill-down works
- No errors

❌ **Test Failed If**:
- Irrelevant responses
- Inaccurate data
- Timeouts
- Drill-down fails
- Errors occur

---

## 📝 Test Results Template

```
Date: [Date]
Tester: [Name]

Prompts Tested: [Number]
Successful: [Number]
Failed: [Number]
Success Rate: [%]

Issues Found:
- [Issue 1]
- [Issue 2]

Recommendations:
- [Recommendation 1]
- [Recommendation 2]
```

---

## 🔗 Related Documents

- `COPILOT_TEST_PROMPTS.md` - 53 test prompts
- `COPILOT_QUICK_TEST_GUIDE.md` - Detailed quick start
- `COPILOT_INTERACTIVE_TEST_SCENARIOS.md` - 10 scenarios
- `COPILOT_TESTING_SUMMARY.md` - Complete guide

---

## 💡 Pro Tips

1. **Start Simple**: Begin with basic questions
2. **Test Drill-Down**: Select entities and ask specific questions
3. **Click Follow-Ups**: Use suggested follow-up questions
4. **Check Data**: Verify answers match dashboard
5. **Note Issues**: Document any problems
6. **Test Edge Cases**: Ask unclear or complex questions

---

## 🚀 Quick Start (30 seconds)

```bash
# 1. Open dashboard
http://localhost:3000

# 2. Click "Ask Copilot"

# 3. Paste this:
What is the current planning health?

# 4. Press Enter

# 5. Observe response
```

---

## 📞 Support

If issues occur:
1. Check browser console (F12)
2. Check backend logs
3. Verify backend running: `func start`
4. Verify frontend running: `npm start`
5. Try clearing cache: Ctrl+Shift+Delete

---

## ⏱️ Time Estimates

| Test | Time |
|------|------|
| Quick Test | 5 min |
| Extended Test | 10 min |
| Drill-Down | 5 min |
| Scenario 1 | 10 min |
| Scenario 2-5 | 15 min each |
| Edge Cases | 10 min |
| **Total** | **~90 min** |

---

## 🎓 Learning Path

1. **Beginner** (5 min): Quick test
2. **Intermediate** (15 min): Extended test + drill-down
3. **Advanced** (30 min): Scenarios 1-3
4. **Expert** (60 min): All scenarios + edge cases

---

## ✨ Key Features to Test

- [ ] Health analysis
- [ ] Forecast tracking
- [ ] Risk assessment
- [ ] Change analysis
- [ ] Supplier impact
- [ ] Design changes
- [ ] Location analysis
- [ ] Material analysis
- [ ] Recommendations
- [ ] Follow-up suggestions
- [ ] Context switching
- [ ] Error handling

---

## 🏆 Final Checklist

- [ ] Copilot opens
- [ ] Responds to prompts
- [ ] Responses are accurate
- [ ] Performance is good
- [ ] Follow-ups work
- [ ] Drill-down works
- [ ] No errors
- [ ] Data matches dashboard

**Ready to test? Start with the 5-minute quick test!**

