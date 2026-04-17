# Ollama Integration - Deployment Checklist ✅

**Status**: Ready for deployment  
**Date**: April 17, 2026  
**Estimated Time**: 3.5 hours

---

## 📋 Pre-Deployment Checklist

### Code Review
- [ ] Read `OLLAMA_INTEGRATION_COMPLETE_FINAL.md`
- [ ] Review `planning_intelligence/ollama_llm_service.py`
- [ ] Review updated `planning_intelligence/function_app.py`
- [ ] Verify all 12 functions are updated
- [ ] Check error handling and fallback logic

### Environment Setup
- [ ] Verify hardware (8+ GB RAM)
- [ ] Check network connectivity
- [ ] Confirm Ollama installation path
- [ ] Verify Python 3.9+ installed
- [ ] Check Azure Function App access

### Documentation Review
- [ ] Read integration guide
- [ ] Review cost comparison
- [ ] Understand fallback logic
- [ ] Know troubleshooting steps
- [ ] Have support contacts ready

---

## 🚀 Installation Phase (15 minutes)

### Step 1: Install Ollama
- [ ] Download Ollama from https://ollama.ai/download
- [ ] Run installer
- [ ] Restart computer if required
- [ ] Verify installation: `ollama --version`

### Step 2: Pull Model
- [ ] Open terminal/command prompt
- [ ] Run: `ollama pull mistral` (or `ollama pull llama2`)
- [ ] Wait for download to complete (5-10 minutes)
- [ ] Verify: `ollama list`

### Step 3: Start Ollama Server
- [ ] Run: `ollama serve`
- [ ] Verify output: "Listening on 127.0.0.1:11434"
- [ ] Keep terminal open (or run as service)
- [ ] Test: `curl http://localhost:11434/api/tags`

---

## 🔧 Integration Phase (30 minutes)

### Step 1: Copy Files
- [ ] Copy `ollama_llm_service.py` to `planning_intelligence/`
- [ ] Verify file exists and is readable
- [ ] Check file permissions

### Step 2: Update Function App
- [ ] Update `planning_intelligence/function_app.py`
- [ ] Verify imports are correct
- [ ] Check `get_llm_service()` helper is present
- [ ] Verify all 12 functions use new helper
- [ ] No syntax errors

### Step 3: Update Environment
- [ ] Set `OLLAMA_MODEL=mistral` (or llama2)
- [ ] Set `OLLAMA_BASE_URL=http://localhost:11434`
- [ ] Verify environment variables are set
- [ ] Test environment variable access

### Step 4: Update Requirements
- [ ] Verify `requests` is in requirements.txt
- [ ] No new dependencies needed
- [ ] Run: `pip install -r requirements.txt`

---

## ✅ Testing Phase (45 minutes)

### Unit Tests
- [ ] Test Ollama service directly
- [ ] Test connection to Ollama
- [ ] Test model availability
- [ ] Test error handling

### Integration Tests
- [ ] Test all 12 question types
- [ ] Verify response quality
- [ ] Check response time
- [ ] Validate business rules applied

### Functional Tests
- [ ] Test health status question
- [ ] Test forecast question
- [ ] Test risk assessment question
- [ ] Test design change question
- [ ] Test general planning question
- [ ] Test greeting question
- [ ] Test design specification question
- [ ] Test schedule question
- [ ] Test location question
- [ ] Test material question
- [ ] Test entity question
- [ ] Test comparison question

### Performance Tests
- [ ] Measure response time (target: < 5 sec)
- [ ] Check accuracy (target: 85%+)
- [ ] Verify uptime (target: 99%+)
- [ ] Monitor resource usage

### Fallback Tests
- [ ] Stop Ollama server
- [ ] Verify system falls back to Azure
- [ ] Restart Ollama
- [ ] Verify system uses Ollama again

---

## 🚀 Deployment Phase (30 minutes)

### Pre-Deployment
- [ ] Backup current function_app.py
- [ ] Backup current llm_service.py
- [ ] Create deployment plan
- [ ] Notify stakeholders

### Deployment
- [ ] Deploy updated function_app.py
- [ ] Deploy ollama_llm_service.py
- [ ] Update environment variables
- [ ] Restart Azure Function App
- [ ] Verify deployment successful

### Post-Deployment
- [ ] Monitor logs for errors
- [ ] Check response times
- [ ] Verify all functions working
- [ ] Gather initial feedback
- [ ] Document any issues

---

## 📊 Monitoring Phase (Ongoing)

### Daily Monitoring
- [ ] Check Ollama is running
- [ ] Monitor response times
- [ ] Check error logs
- [ ] Verify uptime

### Weekly Monitoring
- [ ] Review performance metrics
- [ ] Check user feedback
- [ ] Analyze cost savings
- [ ] Identify optimization opportunities

### Monthly Monitoring
- [ ] Generate performance report
- [ ] Calculate cost savings
- [ ] Plan optimizations
- [ ] Update documentation

---

## 🎯 Success Criteria

### Performance
- [ ] Response time: < 5 seconds
- [ ] Accuracy: 85%+ correct responses
- [ ] Uptime: 99%+
- [ ] All 12 question types working

### Cost
- [ ] No Azure OpenAI costs
- [ ] Hardware cost: $1,500 (one-time)
- [ ] Annual savings: $6,000-12,000

### User Satisfaction
- [ ] User satisfaction: 4+ stars
- [ ] Adoption rate: 80%+
- [ ] No complaints about quality

---

## 🔄 Rollback Plan

### If Issues Occur
1. [ ] Stop Ollama server
2. [ ] System automatically uses Azure OpenAI
3. [ ] Investigate issue
4. [ ] Fix and restart Ollama
5. [ ] Resume normal operation

### If Rollback Needed
1. [ ] Restore backup of function_app.py
2. [ ] Remove ollama_llm_service.py
3. [ ] Restart Azure Function App
4. [ ] Verify Azure OpenAI working
5. [ ] Investigate root cause

---

## 📞 Support Contacts

### Ollama Support
- Website: https://ollama.ai
- GitHub: https://github.com/jmorganca/ollama
- Discord: https://discord.gg/ollama

### Azure Support
- Portal: https://portal.azure.com
- Support: Azure Support Plan
- Documentation: https://docs.microsoft.com/azure

### Internal Support
- Technical Lead: [Name]
- DevOps: [Name]
- Product Owner: [Name]

---

## 📋 Sign-Off

### Technical Review
- [ ] Code reviewed and approved
- [ ] Tests passed
- [ ] Performance acceptable
- [ ] Security verified

### Business Review
- [ ] Cost savings confirmed
- [ ] Timeline acceptable
- [ ] Risk assessment complete
- [ ] Stakeholders informed

### Deployment Approval
- [ ] Technical Lead: _________________ Date: _______
- [ ] Product Owner: _________________ Date: _______
- [ ] DevOps Lead: _________________ Date: _______

---

## 📊 Deployment Summary

| Phase | Duration | Status |
|-------|----------|--------|
| Installation | 15 min | ⏳ Pending |
| Integration | 30 min | ⏳ Pending |
| Testing | 45 min | ⏳ Pending |
| Deployment | 30 min | ⏳ Pending |
| Monitoring | Ongoing | ⏳ Pending |
| **Total** | **2 hours** | ⏳ Pending |

---

## 🎓 Key Reminders

1. **Ollama Must Be Running**: System won't work if Ollama is not running
2. **Model Must Be Pulled**: Download model before starting Ollama
3. **Environment Variables**: Set OLLAMA_MODEL and OLLAMA_BASE_URL
4. **Fallback Available**: Azure OpenAI will be used if Ollama unavailable
5. **Monitor Performance**: Watch response times and accuracy
6. **Gather Feedback**: Collect user feedback for optimization

---

## ✨ Ready to Deploy?

**Checklist Complete?** ✅ Yes → Proceed to deployment  
**Issues Found?** ❌ No → Resolve before deployment  
**Questions?** → Review OLLAMA_INTEGRATION_COMPLETE_FINAL.md

---

**Status**: ✅ Ready for Deployment  
**Estimated Time**: 2 hours  
**Cost Savings**: $6,000-12,000/year  
**Last Updated**: April 17, 2026

---

**Next Step**: Start with Installation Phase
