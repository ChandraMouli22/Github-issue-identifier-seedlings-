# 🚀 Deployment Guide - Render.com

This guide will help you deploy the GitHub Issue Analyzer to Render.com in under 5 minutes.

## 📋 Prerequisites

Before deploying, ensure you have:

1. ✅ A [GitHub account](https://github.com) with this repository pushed
2. ✅ A [Render.com account](https://render.com) (free tier available)
3. ✅ **Google Gemini API Key** - Get it at [Google AI Studio](https://makersuite.google.com/app/apikey)
4. ✅ **Hugging Face API Key** (optional) - Get it at [Hugging Face Settings](https://huggingface.co/settings/tokens)
5. ✅ **GitHub Token** (optional) - Generate at [GitHub Settings](https://github.com/settings/tokens)

---

## 🎯 Quick Deploy (Automated)

### Option 1: Using render.yaml (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Render deployment config"
   git push origin main
   ```

2. **Create New Web Service on Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository
   - Render will **auto-detect** `render.yaml` and configure everything

3. **Add Environment Variables**
   
   In the Render dashboard, add these environment variables:
   
   | Key | Value | Required |
   |-----|-------|----------|
   | `LLM_API_KEY` | Your Google Gemini API key | ✅ Yes |
   | `HF_API_KEY` | Your Hugging Face API key | ⚠️ Optional (for HF models) |
   | `GITHUB_TOKEN` | Your GitHub personal access token | ⚠️ Optional (increases rate limits) |

4. **Deploy**
   - Click **"Create Web Service"**
   - Wait 2-3 minutes for the build to complete
   - Your app will be live at `https://your-app-name.onrender.com` 🎉

---

## 🛠️ Manual Deploy (Alternative)

If you prefer manual configuration:

1. **Create New Web Service**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository

2. **Configure Build Settings**
   - **Name:** `github-issue-analyzer` (or your preferred name)
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Add Environment Variables** (same as above)

4. **Advanced Settings**
   - **Health Check Path:** `/health`
   - **Auto-Deploy:** `Yes` (deploys automatically on git push)

5. **Create Web Service**

---

## 🔐 Environment Variables Setup

### Required Variables

#### `LLM_API_KEY` (Required)
- **What:** Google Gemini API Key
- **Get it:** [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Why:** Required for AI analysis with Gemini models

### Optional Variables

#### `HF_API_KEY` (Optional)
- **What:** Hugging Face API Token
- **Get it:** [Hugging Face Settings](https://huggingface.co/settings/tokens)
- **Why:** Required only if using DeepSeek R1 or Llama 3.1 models
- **Note:** For Llama 3.1, you must accept the model license on Hugging Face

#### `GITHUB_TOKEN` (Optional but Recommended)
- **What:** GitHub Personal Access Token
- **Get it:** [GitHub Settings → Tokens](https://github.com/settings/tokens)
- **Permissions needed:** `public_repo` (read access to public repositories)
- **Why:** Increases GitHub API rate limit from 60 to 5,000 requests/hour

---

## ✅ Verify Deployment

After deployment completes:

1. **Check Health Endpoint**
   ```
   https://your-app-name.onrender.com/health
   ```
   Should return: `{"status": "ok"}`

2. **Open the App**
   ```
   https://your-app-name.onrender.com
   ```

3. **Test Analysis**
   - Enter: `https://github.com/facebook/react`
   - Issue: `1`
   - Click "Generate Analysis"
   - Should return AI analysis in 3-5 seconds

4. **Check API Docs**
   ```
   https://your-app-name.onrender.com/docs
   ```
   Interactive Swagger UI for testing endpoints

---

## 🐛 Troubleshooting

### Build Fails

**Problem:** `pip install` fails
- **Solution:** Check `requirements.txt` is committed to git
- **Solution:** Ensure Python version is 3.10+ in Render settings

### App Crashes on Startup

**Problem:** `Application startup failed`
- **Solution:** Check environment variables are set correctly
- **Solution:** Verify `LLM_API_KEY` is valid
- **Solution:** Check Render logs for specific error messages

### API Returns 500 Errors

**Problem:** Analysis fails with server error
- **Solution:** Verify `LLM_API_KEY` is set and valid
- **Solution:** Check Render logs: Dashboard → Your Service → Logs
- **Solution:** Test API key locally first

### Rate Limit Errors

**Problem:** "Rate limit exceeded" errors
- **Solution:** Add `GITHUB_TOKEN` to increase GitHub API limits
- **Solution:** Use caching - analyze same issue twice (second time is instant)
- **Solution:** Try different AI models (switch from Gemini to Hugging Face)

### Slow Cold Starts

**Problem:** First request takes 30+ seconds
- **Solution:** This is normal on Render's free tier (spins down after inactivity)
- **Solution:** Upgrade to paid tier for always-on instances
- **Solution:** Use Render's "Keep Alive" feature (paid plans)

---

## 📊 Monitoring

### View Logs
```
Render Dashboard → Your Service → Logs
```

### Check Metrics
```
Render Dashboard → Your Service → Metrics
```
- Request count
- Response times
- Memory usage
- CPU usage

---

## 🔄 Continuous Deployment

With `autoDeploy: true` in `render.yaml`:

1. Make changes to your code
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```
3. Render **automatically** detects the push and redeploys
4. Wait 2-3 minutes for build to complete
5. Changes are live! 🎉

---

## 💰 Cost

**Free Tier Limits:**
- ✅ 750 hours/month (enough for 1 always-on service)
- ✅ Automatic SSL certificates
- ✅ Unlimited bandwidth
- ⚠️ Spins down after 15 minutes of inactivity
- ⚠️ Cold start time: ~30 seconds

**Paid Tier ($7/month):**
- ✅ No spin-down (always-on)
- ✅ Faster builds
- ✅ More resources

---

## 🎯 Next Steps

After successful deployment:

1. ✅ **Test thoroughly** - Try analyzing multiple issues
2. ✅ **Monitor logs** - Check for any errors
3. ✅ **Set up custom domain** (optional) - Render supports custom domains
4. ✅ **Enable auto-deploy** - Push to GitHub = automatic deployment
5. ✅ **Share your app** - Send the URL to users!

---

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Render Community Forum](https://community.render.com)

---

## 🆘 Need Help?

If you encounter issues:

1. Check Render logs first
2. Review this troubleshooting section
3. Check [Render Status Page](https://status.render.com)
4. Ask in [Render Community](https://community.render.com)

---

**🎉 Congratulations! Your GitHub Issue Analyzer is now live on the internet!**
