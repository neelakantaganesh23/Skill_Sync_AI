import React, { useState, useRef } from 'react';
import { 
  Upload, 
  FileText, 
  Target, 
  BarChart3, 
  CheckCircle, 
  AlertTriangle, 
  Download,
  ArrowLeft,
  Loader2,
  Star,
  TrendingUp,
  Clock,
  Lightbulb,
  Award,
  Settings
} from 'lucide-react';

const ATSToolApp = () => {
  const [currentStep, setCurrentStep] = useState('upload'); // upload, analyzing, results
  const [uploadedFile, setUploadedFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [showSettings, setShowSettings] = useState(false);
  const [demoMode, setDemoMode] = useState(true); // Toggle for demo/real API
  const fileInputRef = useRef(null);

  // Generate dynamic demo results based on content
  const generateDemoResults = () => {
    const jdLower = jobDescription.toLowerCase();
    const fileName = uploadedFile?.name.toLowerCase() || '';
    
    // Base score influenced by content
    let baseScore = 65;
    
    // Check for common keywords and adjust score
    const techKeywords = ['javascript', 'react', 'python', 'java', 'aws', 'docker', 'sql', 'git'];
    const managementKeywords = ['project management', 'team lead', 'scrum', 'agile', 'leadership'];
    const experienceKeywords = ['years', 'experience', 'senior', 'lead', 'manager'];
    
    const foundTechKeywords = techKeywords.filter(keyword => 
      jdLower.includes(keyword) || fileName.includes(keyword)
    );
    const foundMgmtKeywords = managementKeywords.filter(keyword => 
      jdLower.includes(keyword)
    );
    const foundExpKeywords = experienceKeywords.filter(keyword => 
      jdLower.includes(keyword)
    );
    
    // Adjust score based on matches
    baseScore += foundTechKeywords.length * 3;
    baseScore += foundMgmtKeywords.length * 2;
    baseScore += foundExpKeywords.length * 2;
    baseScore += Math.floor(jobDescription.length / 100); // Longer JD = more detailed
    
    // Cap at 95 to keep it realistic
    baseScore = Math.min(95, baseScore);
    
    // Generate category scores around the base score
    const variance = 15;
    const categoryScores = {
      keyword_matching: Math.max(30, Math.min(100, baseScore + (Math.random() - 0.5) * variance)),
      skills_alignment: Math.max(40, Math.min(100, baseScore + (Math.random() - 0.5) * variance)),
      experience_relevance: Math.max(35, Math.min(100, baseScore + (Math.random() - 0.5) * variance)),
      format_optimization: Math.max(50, Math.min(100, baseScore + (Math.random() - 0.5) * variance)),
      content_quality: Math.max(45, Math.min(100, baseScore + (Math.random() - 0.5) * variance))
    };
    
    // Calculate overall score as average
    const overallScore = Math.round(Object.values(categoryScores).reduce((a, b) => a + b, 0) / 5);
    
    // Generate contextual strengths and gaps
    const strengths = [];
    const gaps = [];
    const missingSkills = [];
    
    if (foundTechKeywords.length > 2) {
      strengths.push('Strong technical skills alignment with job requirements');
    } else {
      gaps.push('Limited technical skills mentioned in resume');
      missingSkills.push(...techKeywords.slice(0, 3));
    }
    
    if (foundMgmtKeywords.length > 0) {
      strengths.push('Leadership and project management experience evident');
    } else {
      gaps.push('Lack of leadership or project management keywords');
      missingSkills.push('Project Management', 'Team Leadership');
    }
    
    if (jobDescription.length > 500) {
      strengths.push('Detailed job requirements allow for precise matching');
    }
    
    if (overallScore >= 80) {
      strengths.push('Well-structured resume format');
      strengths.push('Good use of action verbs and metrics');
    } else {
      gaps.push('Resume format could be optimized for ATS systems');
      gaps.push('Consider adding more quantified achievements');
    }
    
    const readinessStatus = overallScore >= 90 ? 'ATS READY' : 
                           overallScore >= 70 ? 'NEEDS MINOR IMPROVEMENTS' : 
                           'NEEDS MAJOR IMPROVEMENTS';
    
    return {
      status: 'success',
      ats_analysis: {
        overall_score: overallScore,
        readiness_status: readinessStatus,
        category_scores: Object.fromEntries(
          Object.entries(categoryScores).map(([key, value]) => [key, Math.round(value)])
        ),
        strengths: strengths,
        gaps: gaps,
        missing_skills: missingSkills.slice(0, 5),
        detailed_analysis: {
          keyword_density: `Found ${foundTechKeywords.length + foundMgmtKeywords.length} relevant keywords`,
          content_structure: overallScore > 75 ? 'Good structure with clear sections' : 'Structure could be improved',
          ats_compatibility: overallScore > 80 ? 'High ATS compatibility' : 'Moderate ATS compatibility'
        }
      },
      improvement_plan: overallScore < 90 ? {
        priority_improvements: [
          {
            skill: missingSkills[0] || 'Technical Skills',
            category: 'Technical Skills',
            current_level: 'Basic',
            target_level: 'Intermediate',
            time_estimate: '2-3 months',
            learning_path: [
              `Learn ${missingSkills[0] || 'relevant technical skills'}`,
              'Complete relevant certifications',
              'Build portfolio projects'
            ],
            resources: [
              { title: 'Online Course', provider: 'Coursera', duration: '20 hours' },
              { title: 'Practice Platform', provider: 'Various', duration: '40 hours' }
            ]
          }
        ],
        quick_wins: [
          {
            action: 'Add missing keywords',
            time_required: '30 minutes',
            impact: 'High',
            description: `Include keywords: ${missingSkills.slice(0, 3).join(', ')}`
          },
          {
            action: 'Optimize resume format',
            time_required: '1 hour',
            impact: 'Medium',
            description: 'Ensure ATS-friendly formatting and structure'
          }
        ]
      } : null
    };
  };

  // Real ATS analysis function
  const analyzeResume = async () => {
    setIsAnalyzing(true);
    setCurrentStep('analyzing');
    setAnalysisProgress(0);

    try {
      // Progress updates
      const updateProgress = (progress, message) => {
        setAnalysisProgress(progress);
      };

      updateProgress(10, 'Initializing analysis...');
      await new Promise(resolve => setTimeout(resolve, 800));
      
      if (demoMode) {
        // Demo mode - generate dynamic results
        updateProgress(30, 'Extracting resume data...');
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        updateProgress(60, 'Calculating ATS scores...');
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        updateProgress(80, 'Generating recommendations...');
        await new Promise(resolve => setTimeout(resolve, 800));
        
        updateProgress(100, 'Analysis complete!');
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const results = generateDemoResults();
        setAnalysisResults(results);
        
      } else {
        // Real API mode
        const formData = new FormData();
        formData.append('resume', uploadedFile);
        formData.append('job_description', jobDescription);
        formData.append('api_key', apiKey);

        updateProgress(30, 'Extracting resume data...');

        const response = await fetch('/api/analyze-resume', {
          method: 'POST',
          body: formData,
        });

        updateProgress(60, 'Calculating ATS scores...');

        if (!response.ok) {
          throw new Error(`Analysis failed: ${response.statusText}`);
        }

        const results = await response.json();
        
        updateProgress(80, 'Generating recommendations...');
        
        if (!results || !results.ats_analysis) {
          throw new Error('Invalid response format from analysis API');
        }

        updateProgress(100, 'Analysis complete!');
        await new Promise(resolve => setTimeout(resolve, 500));

        setAnalysisResults(results);
      }
      
      setIsAnalyzing(false);
      setCurrentStep('results');

    } catch (error) {
      console.error('Analysis error:', error);
      setIsAnalyzing(false);
      
      setAnalysisResults({
        status: 'error',
        error_message: error.message || 'Analysis failed. Please try again.',
        ats_analysis: {
          overall_score: 0,
          readiness_status: 'ERROR',
          category_scores: {},
          strengths: [],
          gaps: ['Analysis failed - please check your API key and try again'],
          missing_skills: []
        }
      });
      setCurrentStep('results');
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      setUploadedFile(file);
    } else {
      alert('Please upload a PDF file');
    }
  };

  const ScoreGauge = ({ score, title, size = 'large' }) => {
    const radius = size === 'large' ? 60 : 40;
    const strokeWidth = size === 'large' ? 8 : 6;
    const normalizedRadius = radius - strokeWidth * 2;
    const circumference = normalizedRadius * 2 * Math.PI;
    const strokeDasharray = `${(score / 100) * circumference} ${circumference}`;
    
    const getScoreColor = (score) => {
      if (score >= 90) return '#10b981';
      if (score >= 70) return '#f59e0b';
      return '#ef4444';
    };

    return (
      <div className="flex flex-col items-center">
        <div className="relative">
          <svg height={radius * 2} width={radius * 2} className="transform -rotate-90">
            <circle
              stroke="#e5e7eb"
              fill="transparent"
              strokeWidth={strokeWidth}
              r={normalizedRadius}
              cx={radius}
              cy={radius}
            />
            <circle
              stroke={getScoreColor(score)}
              fill="transparent"
              strokeWidth={strokeWidth}
              strokeDasharray={strokeDasharray}
              strokeLinecap="round"
              r={normalizedRadius}
              cx={radius}
              cy={radius}
              className="transition-all duration-1000 ease-out"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className={`font-bold ${size === 'large' ? 'text-2xl' : 'text-lg'}`}>
                {score}
              </div>
              <div className={`text-gray-500 ${size === 'large' ? 'text-sm' : 'text-xs'}`}>
                /100
              </div>
            </div>
          </div>
        </div>
        <div className={`mt-2 text-center font-medium ${size === 'large' ? 'text-lg' : 'text-sm'}`}>
          {title}
        </div>
      </div>
    );
  };

  const CategoryBar = ({ category, score }) => (
    <div className="mb-4">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-medium text-gray-700 capitalize">
          {category.replace('_', ' ')}
        </span>
        <span className="text-sm font-bold text-gray-900">{score}/100</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-1000 ${
            score >= 90 ? 'bg-green-500' : score >= 70 ? 'bg-yellow-500' : 'bg-red-500'
          }`}
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );

  const renderUploadStep = () => (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-12">
        <div className="flex items-center justify-center mb-4">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-4 rounded-full">
            <Target className="w-8 h-8 text-white" />
          </div>
        </div>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
          AI-Powered ATS Tool
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Optimize your resume for Applicant Tracking Systems with AI-powered analysis
        </p>
      </div>

      {/* Settings Toggle */}
      <div className="mb-6 flex justify-end">
        <button
          onClick={() => setShowSettings(!showSettings)}
          className="flex items-center px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
        >
          <Settings className="w-4 h-4 mr-2" />
          Settings
        </button>
      </div>

      {/* API Key Configuration */}
      {showSettings && (
        <div className="bg-gray-50 rounded-lg p-6 mb-8">
          <h3 className="text-lg font-semibold mb-4">Configuration</h3>
          
          {/* Demo Mode Toggle */}
          <div className="mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={demoMode}
                onChange={(e) => setDemoMode(e.target.checked)}
                className="mr-2"
              />
              <span className="text-sm font-medium text-gray-700">
                Demo Mode (generates dynamic results based on content)
              </span>
            </label>
            <p className="text-xs text-gray-500 mt-1">
              Enable for testing without API. Disable to use real ATS analysis.
            </p>
          </div>

          {!demoMode && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Gemini API Key
              </label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Enter your Gemini API key"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-sm text-gray-500 mt-1">
                Get your API key from <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Google AI Studio</a>
              </p>
            </div>
          )}
        </div>
      )}

      {/* Main Upload Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Resume Upload */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="flex items-center mb-6">
            <FileText className="w-6 h-6 text-blue-600 mr-3" />
            <h2 className="text-2xl font-bold text-gray-800">Upload Resume</h2>
          </div>
          
          <div
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all ${
              uploadedFile 
                ? 'border-green-400 bg-green-50' 
                : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileUpload}
              className="hidden"
            />
            
            {uploadedFile ? (
              <div className="text-center">
                <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
                <p className="text-lg font-semibold text-green-700">
                  {uploadedFile.name}
                </p>
                <p className="text-sm text-green-600 mt-2">
                  {(uploadedFile.size / 1024).toFixed(1)} KB
                </p>
              </div>
            ) : (
              <div className="text-center">
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-lg font-semibold text-gray-700">
                  Drop your PDF resume here
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  or click to browse files
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Job Description */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="flex items-center mb-6">
            <Target className="w-6 h-6 text-purple-600 mr-3" />
            <h2 className="text-2xl font-bold text-gray-800">Job Description</h2>
          </div>
          
          <textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the complete job description including required skills, responsibilities, and qualifications..."
            className="w-full h-64 p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
          />
          
          {jobDescription && (
            <div className="mt-4 text-sm text-gray-600">
              <span className="font-medium">Word count:</span> {jobDescription.split(' ').length} words
            </div>
          )}
        </div>
      </div>

      {/* Analyze Button */}
      {uploadedFile && jobDescription && (demoMode || apiKey) && (
        <div className="mt-12 text-center">
          <button
            onClick={analyzeResume}
            className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-12 py-4 rounded-full text-lg font-semibold hover:from-blue-700 hover:to-purple-700 transform hover:scale-105 transition-all duration-200 shadow-lg"
          >
            🚀 Analyze Resume {demoMode && '(Demo)'}
          </button>
        </div>
      )}

      {(!uploadedFile || !jobDescription || (!demoMode && !apiKey)) && (
        <div className="mt-8 text-center">
          <p className="text-gray-500">
            {!uploadedFile ? 'Upload a resume' : ''}
            {!uploadedFile && !jobDescription ? ' and ' : ''}
            {!jobDescription ? 'enter a job description' : ''}
            {(!demoMode && !apiKey) ? ' and configure your API key' : ''}
            {' to start the analysis.'}
          </p>
          {demoMode && (
            <p className="text-sm text-blue-600 mt-2">
              Demo mode is enabled - results will vary based on your resume and job description content
            </p>
          )}
        </div>
      )}
    </div>
  );

  const renderAnalyzingStep = () => (
    <div className="max-w-2xl mx-auto p-6 text-center">
      <div className="bg-white rounded-xl shadow-lg p-12">
        <div className="mb-8">
          <div className="relative">
            <div className="w-24 h-24 mx-auto bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mb-6">
              <Loader2 className="w-12 h-12 text-white animate-spin" />
            </div>
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">
            Analyzing Your Resume
          </h2>
          <p className="text-gray-600 mb-8">
            Our AI is processing your resume and comparing it with the job requirements
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Progress</span>
            <span className="text-sm font-bold text-gray-900">{analysisProgress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="h-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full transition-all duration-500"
              style={{ width: `${analysisProgress}%` }}
            />
          </div>
        </div>

        {/* Analysis Steps */}
        <div className="text-left space-y-3">
          {[
            { step: 'Extracting resume content', progress: 30 },
            { step: 'Analyzing job requirements', progress: 60 },
            { step: 'Calculating ATS scores', progress: 80 },
            { step: 'Generating recommendations', progress: 100 }
          ].map((item, index) => (
            <div key={index} className="flex items-center">
              <div className={`w-4 h-4 rounded-full mr-3 ${
                analysisProgress >= item.progress 
                  ? 'bg-green-500' 
                  : analysisProgress > item.progress - 30 
                  ? 'bg-blue-500' 
                  : 'bg-gray-300'
              }`} />
              <span className={`text-sm ${
                analysisProgress >= item.progress ? 'text-green-700 font-medium' : 'text-gray-600'
              }`}>
                {item.step}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderResults = () => {
    if (!analysisResults) return null;

    // Handle both successful and error responses
    const ats_analysis = analysisResults.ats_analysis || {};
    const { overall_score, readiness_status, category_scores, strengths, gaps, missing_skills } = ats_analysis;
    const improvement_plan = analysisResults.improvement_plan;

    // Show error state if analysis failed
    if (analysisResults.status === 'error') {
      return (
        <div className="max-w-4xl mx-auto p-6">
          <div className="bg-red-50 border border-red-200 rounded-xl p-8 text-center">
            <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-red-800 mb-4">Analysis Failed</h2>
            <p className="text-red-700 mb-6">{analysisResults.error_message}</p>
            <button
              onClick={() => {
                setCurrentStep('upload');
                setAnalysisResults(null);
              }}
              className="bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      );
    }

    return (
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={() => {
              setCurrentStep('upload');
              setAnalysisResults(null);
              setUploadedFile(null);
              setJobDescription('');
            }}
            className="flex items-center px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            New Analysis
          </button>
          
          <h1 className="text-3xl font-bold text-gray-800">ATS Analysis Results</h1>
          
          <button className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
        </div>

        {/* Overall Score */}
        <div className={`rounded-xl p-8 mb-8 text-center text-white ${
          overall_score >= 90 
            ? 'bg-gradient-to-r from-green-500 to-green-600' 
            : overall_score >= 70 
            ? 'bg-gradient-to-r from-yellow-500 to-orange-500' 
            : 'bg-gradient-to-r from-red-500 to-red-600'
        }`}>
          <div className="text-6xl font-bold mb-4">{overall_score}/100</div>
          <div className="text-2xl font-semibold mb-2">Overall ATS Score</div>
          <div className="text-lg opacity-90">Status: {readiness_status}</div>
        </div>

        {/* Score Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Gauge Chart */}
          <div className="bg-white rounded-xl shadow-lg p-8">
            <h3 className="text-xl font-bold text-gray-800 mb-6 text-center">Overall Score</h3>
            <div className="flex justify-center">
              <ScoreGauge score={overall_score} title="ATS Ready" />
            </div>
          </div>

          {/* Category Scores */}
          <div className="bg-white rounded-xl shadow-lg p-8">
            <h3 className="text-xl font-bold text-gray-800 mb-6">Category Breakdown</h3>
            {Object.entries(category_scores).map(([category, score]) => (
              <CategoryBar key={category} category={category} score={score} />
            ))}
          </div>
        </div>

        {/* Detailed Analysis Tabs */}
        <div className="bg-white rounded-xl shadow-lg">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 p-8">
            {/* Strengths */}
            <div>
              <div className="flex items-center mb-6">
                <CheckCircle className="w-6 h-6 text-green-500 mr-3" />
                <h3 className="text-xl font-bold text-gray-800">Strengths</h3>
              </div>
              <div className="space-y-3">
                {strengths.map((strength, index) => (
                  <div key={index} className="flex items-start p-3 bg-green-50 rounded-lg border-l-4 border-green-500">
                    <Star className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                    <span className="text-green-800">{strength}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Areas for Improvement */}
            <div>
              <div className="flex items-center mb-6">
                <AlertTriangle className="w-6 h-6 text-yellow-500 mr-3" />
                <h3 className="text-xl font-bold text-gray-800">Areas for Improvement</h3>
              </div>
              <div className="space-y-3">
                {gaps.map((gap, index) => (
                  <div key={index} className="flex items-start p-3 bg-yellow-50 rounded-lg border-l-4 border-yellow-500">
                    <TrendingUp className="w-5 h-5 text-yellow-500 mr-3 mt-0.5 flex-shrink-0" />
                    <span className="text-yellow-800">{gap}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Missing Skills */}
          {missing_skills.length > 0 && (
            <div className="border-t px-8 py-6">
              <div className="flex items-center mb-4">
                <Lightbulb className="w-6 h-6 text-blue-500 mr-3" />
                <h3 className="text-xl font-bold text-gray-800">Missing Skills</h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {missing_skills.map((skill, index) => (
                  <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Improvement Plan */}
        {improvement_plan && (
          <div className="mt-8 bg-white rounded-xl shadow-lg p-8">
            <div className="flex items-center mb-6">
              <Award className="w-6 h-6 text-purple-500 mr-3" />
              <h3 className="text-2xl font-bold text-gray-800">Improvement Plan</h3>
            </div>

            {/* Quick Wins */}
            <div className="mb-8">
              <h4 className="text-lg font-semibold text-gray-800 mb-4">⚡ Quick Wins</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {improvement_plan.quick_wins?.map((win, index) => (
                  <div key={index} className="p-4 bg-green-50 rounded-lg border border-green-200">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-green-800">{win.action}</span>
                      <span className="text-sm text-green-600 flex items-center">
                        <Clock className="w-4 h-4 mr-1" />
                        {win.time_required}
                      </span>
                    </div>
                    <p className="text-sm text-green-700 mb-2">{win.description}</p>
                    <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                      win.impact === 'High' ? 'bg-red-100 text-red-800' :
                      win.impact === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {win.impact} Impact
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Priority Improvements */}
            <div>
              <h4 className="text-lg font-semibold text-gray-800 mb-4">🎯 Priority Improvements</h4>
              <div className="space-y-6">
                {improvement_plan.priority_improvements?.map((improvement, index) => (
                  <div key={index} className="p-6 bg-gray-50 rounded-lg">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h5 className="text-lg font-semibold text-gray-800">{improvement.skill}</h5>
                        <p className="text-sm text-gray-600">
                          {improvement.current_level} → {improvement.target_level}
                        </p>
                      </div>
                      <span className="text-sm text-blue-600 font-medium">{improvement.time_estimate}</span>
                    </div>
                    
                    <div className="mb-4">
                      <h6 className="font-medium text-gray-700 mb-2">Learning Path:</h6>
                      <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                        {improvement.learning_path?.map((step, stepIndex) => (
                          <li key={stepIndex}>{step}</li>
                        ))}
                      </ul>
                    </div>

                    <div>
                      <h6 className="font-medium text-gray-700 mb-2">Recommended Resources:</h6>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {improvement.resources?.map((resource, resourceIndex) => (
                          <div key={resourceIndex} className="p-3 bg-white rounded border">
                            <div className="font-medium text-gray-800">{resource.title}</div>
                            <div className="text-sm text-gray-600">{resource.provider} • {resource.duration}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {currentStep === 'upload' && renderUploadStep()}
      {currentStep === 'analyzing' && renderAnalyzingStep()}
      {currentStep === 'results' && renderResults()}
    </div>
  );
};

export default ATSToolApp;