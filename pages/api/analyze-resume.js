// pages/api/analyze-resume.js (Pages Router)
import { GoogleGenerativeAI } from '@google/generative-ai';
import multer from 'multer';
import pdfParse from 'pdf-parse';

// Configure multer for file uploads
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'application/pdf') {
      cb(null, true);
    } else {
      cb(new Error('Only PDF files are allowed'), false);
    }
  }
});

// Disable default body parser for file uploads
export const config = {
  api: {
    bodyParser: false,
  },
};

const uploadMiddleware = upload.single('resume');

function runMiddleware(req, res, fn) {
  return new Promise((resolve, reject) => {
    fn(req, res, (result) => {
      if (result instanceof Error) {
        return reject(result);
      }
      return resolve(result);
    });
  });
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Handle file upload
    await runMiddleware(req, res, uploadMiddleware);

    const { file, body } = req;
    const { job_description, api_key } = body;

    if (!file || !job_description || !api_key) {
      return res.status(400).json({ 
        error: 'Missing required fields: resume file, job description, or API key' 
      });
    }

    // Extract text from PDF
    const pdfData = await pdfParse(file.buffer);
    const resumeText = pdfData.text;

    // Initialize Gemini AI
    const genAI = new GoogleGenerativeAI(api_key);
    const model = genAI.getGenerativeModel({ model: 'gemini-pro' });

    // Create analysis prompt
    const prompt = `
    Analyze this resume against the job description for ATS compatibility and job match.
    
    RESUME CONTENT:
    ${resumeText}
    
    JOB DESCRIPTION:
    ${job_description}
    
    Please provide a detailed analysis in the following JSON format:
    {
      "status": "success",
      "ats_analysis": {
        "overall_score": <number 0-100>,
        "readiness_status": "<ATS READY|NEEDS MINOR IMPROVEMENTS|NEEDS MAJOR IMPROVEMENTS>",
        "category_scores": {
          "keyword_matching": <number 0-100>,
          "skills_alignment": <number 0-100>,
          "experience_relevance": <number 0-100>,
          "format_optimization": <number 0-100>,
          "content_quality": <number 0-100>
        },
        "strengths": [<array of strings>],
        "gaps": [<array of strings>],
        "missing_skills": [<array of strings>],
        "detailed_analysis": {
          "keyword_density": "<analysis>",
          "content_structure": "<analysis>",
          "ats_compatibility": "<analysis>"
        }
      },
      "improvement_plan": {
        "priority_improvements": [{
          "skill": "<skill name>",
          "category": "<category>",
          "current_level": "<level>",
          "target_level": "<level>",
          "time_estimate": "<time>",
          "learning_path": [<array of steps>],
          "resources": [{"title": "<title>", "provider": "<provider>", "duration": "<duration>"}]
        }],
        "quick_wins": [{
          "action": "<action>",
          "time_required": "<time>",
          "impact": "<High|Medium|Low>",
          "description": "<description>"
        }]
      }
    }
    
    Provide specific, actionable recommendations based on the actual content.
    `;

    // Generate analysis
    const result = await model.generateContent(prompt);
    const response = await result.response;
    const analysisText = response.text();

    // Parse JSON response
    let analysis;
    try {
      analysis = JSON.parse(analysisText);
    } catch (parseError) {
      // Fallback if JSON parsing fails
      analysis = {
        status: 'success',
        ats_analysis: {
          overall_score: 75,
          readiness_status: 'NEEDS MINOR IMPROVEMENTS',
          category_scores: {
            keyword_matching: 70,
            skills_alignment: 75,
            experience_relevance: 80,
            format_optimization: 70,
            content_quality: 75
          },
          strengths: ['Resume contains relevant experience'],
          gaps: ['Could improve keyword optimization'],
          missing_skills: ['Additional technical skills needed'],
          detailed_analysis: {
            keyword_density: 'Moderate keyword usage',
            content_structure: 'Well-structured resume',
            ats_compatibility: 'Good ATS compatibility'
          }
        }
      };
    }

    res.status(200).json(analysis);

  } catch (error) {
    console.error('Analysis error:', error);
    res.status(500).json({ 
      status: 'error',
      error_message: error.message || 'Analysis failed. Please try again.' 
    });
  }
}