import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FileUpload } from '@/components/ui/file-upload';
import { AnalysisResults } from '@/components/ui/analysis-results';
import { DebugPanel } from '@/components/ui/debug-panel';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/hooks/use-toast';
import { Loader2, Upload, FileCode, FileText, Shield, CheckCircle, Clock, ArrowLeft, Bug, X } from 'lucide-react';
import { debugFetch } from '@/lib/debug-fetch';

const Dashboard = () => {
  const { toast } = useToast();
  const [oldCode, setOldCode] = useState<File[]>([]);
  const [newCode, setNewCode] = useState<File[]>([]);
  const [oldDocs, setOldDocs] = useState<File[]>([]);
  const [newDocs, setNewDocs] = useState<File[]>([]);
  const [oldBinary, setOldBinary] = useState<File[]>([]);
  const [newBinary, setNewBinary] = useState<File[]>([]);
  const [useBinaryMode, setUseBinaryMode] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [showDebugPanel, setShowDebugPanel] = useState(false);
  const [analysisSteps] = useState([
    { title: "Preparing Analysis", description: "Setting up secure analysis environment" },
    { title: "Decompiling Binaries", description: "Converting binaries to readable code" },
    { title: "Analyzing Code", description: "Comparing firmware code changes" },
    { title: "Analyzing Specs", description: "Processing specification updates" },
    { title: "Validating Compliance", description: "Checking security compliance" },
    { title: "Generating Results", description: "Compiling comprehensive analysis" }
  ]);

  const readFileAsText = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target?.result as string);
      reader.onerror = (e) => reject(e);
      reader.readAsText(file);
    });
  };

  const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

  const decompileBinary = async (file: File): Promise<{assembly: string, decompiled: string}> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await debugFetch('http://localhost:8000/api/v1/decompile', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Decompilation failed: ${response.status}`);
    }

    const result = await response.json();
    
    if (!result.success) {
      throw new Error(`Decompilation failed: ${result.error}`);
    }

    return {
      assembly: result.assembly_code,
      decompiled: result.decompiled_code
    };
  };

  const analyzeFiles = async () => {
    // Validate required files based on mode
    const missingFiles = [];
    
    if (useBinaryMode) {
      if (!oldBinary.length) missingFiles.push("original binary");
      if (!newBinary.length) missingFiles.push("updated binary");
    } else {
      if (!oldCode.length) missingFiles.push("original code");
      if (!newCode.length) missingFiles.push("updated code");
    }
    
    if (!oldDocs.length) missingFiles.push("original specifications");
    if (!newDocs.length) missingFiles.push("updated specifications");
    
    if (missingFiles.length > 0) {
      toast({
        title: "Missing Files",
        description: `Please upload: ${missingFiles.join(", ")}`,
        variant: "destructive",
      });
      return;
    }

    setIsAnalyzing(true);
    setCurrentStep(0);
    try {
      // Step 0: Prepare Analysis
      await sleep(1500);
      setCurrentStep(1);

      let oldCodeText: string;
      let newCodeText: string;

      if (useBinaryMode) {
        // Step 1: Decompile Binaries
        const [oldDecompiled, newDecompiled] = await Promise.all([
          decompileBinary(oldBinary[0]),
          decompileBinary(newBinary[0])
        ]);
        
        oldCodeText = oldDecompiled.decompiled || oldDecompiled.assembly;
        newCodeText = newDecompiled.decompiled || newDecompiled.assembly;
        
        setCurrentStep(2);
      } else {
        // Read text files directly
        oldCodeText = await readFileAsText(oldCode[0]);
        newCodeText = await readFileAsText(newCode[0]);
        setCurrentStep(2);
      }

      // Read specification files
      const oldDocText = await readFileAsText(oldDocs[0]);
      const newDocText = await readFileAsText(newDocs[0]);

      // Step 2: Compare Code
      await sleep(800);
      const codeCompareResponse = await debugFetch('http://localhost:8000/api/v1/compare-code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          old_code: oldCodeText,
          new_code: newCodeText,
          firmware_type: "ATmega328P"
        }),
      });

      if (!codeCompareResponse.ok) {
        throw new Error(`Code comparison failed: ${codeCompareResponse.status}`);
      }

      const codeAnalysis = await codeCompareResponse.json();

      // Step 3: Compare Specifications
      setCurrentStep(3);
      await sleep(800);
      const docCompareResponse = await debugFetch('http://localhost:8000/api/v1/compare-specs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          old_spec: oldDocText,
          new_spec: newDocText,
        }),
      });

      if (!docCompareResponse.ok) {
        throw new Error(`Specification comparison failed: ${docCompareResponse.status}`);
      }

      const docAnalysis = await docCompareResponse.json();

      // Step 4: Validate Compliance
      setCurrentStep(4);
      await sleep(800);
      const complianceResponse = await debugFetch('http://localhost:8000/api/v1/validate-compliance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code_analysis: codeAnalysis,
          spec_analysis: docAnalysis,
        }),
      });

      if (!complianceResponse.ok) {
        throw new Error(`Compliance validation failed: ${complianceResponse.status}`);
      }

      const complianceResults = await complianceResponse.json();

      // Step 5: Generate Results
      setCurrentStep(5);
      await sleep(1000);

      // Combine all results for the frontend
      const combinedResults = {
        code_analysis: codeAnalysis,
        doc_analysis: docAnalysis,
        ...complianceResults
      };

      setResults(combinedResults);
      toast({
        title: "Analysis Complete",
        description: "Your firmware analysis has been completed successfully.",
      });

    } catch (error) {
      console.error('Analysis failed:', error);
      toast({
        title: "Analysis Failed",
        description: "There was an error analyzing your files. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsAnalyzing(false);
      setCurrentStep(0);
    }
  };

  const fileAccept = {
    'text/plain': ['.txt', '.asm', '.c', '.h', '.md'],
    'application/octet-stream': ['.asm'],
    'text/x-c': ['.c'],
    'text/x-h': ['.h'],
  };

  const binaryFileAccept = {
    'application/octet-stream': ['.bin', '.elf', '.exe', '.hex'],
    'application/x-executable': ['.elf'],
    'application/x-msdos-program': ['.exe'],
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8 relative">
            <Button
              variant="outline"
              size="sm"
              onClick={() => window.location.href = '/'}
              className="absolute left-0 top-0"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Home
            </Button>
            <div className="flex items-center justify-center mb-4">
              <img 
                src="/android-chrome-512x512.png" 
                alt="SpecTrace Logo" 
                className="h-12 w-12 rounded-xl mr-3"
              />
              <h1 className="text-3xl font-bold text-primary">SpecTrace Dashboard</h1>
            </div>
            <p className="text-muted-foreground">
              Upload your firmware files and specifications to analyze changes, detect anomalies, and ensure compliance.
            </p>
          </div>

          {!results ? (
            <>
              {/* Mode Toggle */}
              <div className="flex justify-center mb-6">
                <div className="bg-muted p-1 rounded-lg">
                  <button
                    onClick={() => setUseBinaryMode(false)}
                    className={`px-4 py-2 rounded-md transition-colors ${
                      !useBinaryMode 
                        ? 'bg-background shadow-sm text-foreground' 
                        : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    📄 Text Files
                  </button>
                  <button
                    onClick={() => setUseBinaryMode(true)}
                    className={`px-4 py-2 rounded-md transition-colors ${
                      useBinaryMode 
                        ? 'bg-background shadow-sm text-foreground' 
                        : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    🔧 Binary Files
                  </button>
                </div>
              </div>

              {/* Upload Section */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                {/* Old Firmware */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FileCode className="h-5 w-5" />
                      Original Firmware
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {useBinaryMode ? (
                      <>
                        <FileUpload
                          label="Binary Files"
                          description="Upload your original binary firmware (.bin, .elf, .exe, .hex)"
                          files={oldBinary}
                          onFilesChange={setOldBinary}
                          accept={binaryFileAccept}
                        />
                        <FileUpload
                          label="Specifications"
                          description="Upload your original specifications (.txt, .md)"
                          files={oldDocs}
                          onFilesChange={setOldDocs}
                          accept={fileAccept}
                        />
                      </>
                    ) : (
                      <>
                        <FileUpload
                          label="Code Files"
                          description="Upload your original firmware code (.asm, .c, .h)"
                          files={oldCode}
                          onFilesChange={setOldCode}
                          accept={fileAccept}
                        />
                        <FileUpload
                          label="Specifications"
                          description="Upload your original specifications (.txt, .md)"
                          files={oldDocs}
                          onFilesChange={setOldDocs}
                          accept={fileAccept}
                        />
                      </>
                    )}
                  </CardContent>
                </Card>

                {/* New Firmware */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FileCode className="h-5 w-5" />
                      Updated Firmware
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {useBinaryMode ? (
                      <>
                        <FileUpload
                          label="Binary Files"
                          description="Upload your updated binary firmware (.bin, .elf, .exe, .hex)"
                          files={newBinary}
                          onFilesChange={setNewBinary}
                          accept={binaryFileAccept}
                        />
                        <FileUpload
                          label="Specifications"
                          description="Upload your updated specifications (.txt, .md)"
                          files={newDocs}
                          onFilesChange={setNewDocs}
                          accept={fileAccept}
                        />
                      </>
                    ) : (
                      <>
                        <FileUpload
                          label="Code Files"
                          description="Upload your updated firmware code (.asm, .c, .h)"
                          files={newCode}
                          onFilesChange={setNewCode}
                          accept={fileAccept}
                        />
                        <FileUpload
                          label="Specifications"
                          description="Upload your updated specifications (.txt, .md)"
                          files={newDocs}
                          onFilesChange={setNewDocs}
                          accept={fileAccept}
                        />
                      </>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Progress Indicator */}
              {isAnalyzing && (
                <Card className="mb-8 border-secondary/20 bg-gradient-to-r from-secondary/5 to-accent/5">
                  <CardHeader className="pb-4">
                    <CardTitle className="flex items-center gap-3 text-secondary">
                      <Loader2 className="h-5 w-5 animate-spin" />
                      Analysis in Progress
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-4">
                      {analysisSteps.map((step, index) => (
                        <div key={index} className="flex items-center gap-4">
                          <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center border-2 transition-all duration-300 ${
                            index < currentStep 
                              ? 'bg-green-500 border-green-500 text-white' 
                              : index === currentStep 
                                ? 'bg-secondary border-secondary text-white animate-pulse' 
                                : 'bg-muted border-muted-foreground/20 text-muted-foreground'
                          }`}>
                            {index < currentStep ? (
                              <CheckCircle className="h-4 w-4" />
                            ) : index === currentStep ? (
                              <Clock className="h-4 w-4" />
                            ) : (
                              <span className="text-sm font-medium">{index + 1}</span>
                            )}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className={`font-medium transition-colors duration-300 ${
                              index <= currentStep ? 'text-foreground' : 'text-muted-foreground'
                            }`}>
                              {step.title}
                            </div>
                            <div className={`text-sm transition-colors duration-300 ${
                              index <= currentStep ? 'text-muted-foreground' : 'text-muted-foreground/60'
                            }`}>
                              {step.description}
                            </div>
                          </div>
                          {index === currentStep && (
                            <Loader2 className="h-4 w-4 animate-spin text-secondary" />
                          )}
                        </div>
                      ))}
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Progress</span>
                        <span className="font-medium text-secondary">{Math.round((currentStep / (analysisSteps.length - 1)) * 100)}%</span>
                      </div>
                      <Progress 
                        value={(currentStep / (analysisSteps.length - 1)) * 100} 
                        className="h-2 bg-muted"
                      />
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Analyze Button */}
              <div className="text-center">
                <Button
                  onClick={analyzeFiles}
                  disabled={isAnalyzing || 
                    (useBinaryMode 
                      ? (!oldBinary.length || !newBinary.length || !oldDocs.length || !newDocs.length)
                      : (!oldCode.length || !newCode.length || !oldDocs.length || !newDocs.length)
                    )
                  }
                  size="lg"
                  className="bg-gradient-to-r from-secondary to-accent hover:from-secondary/90 hover:to-accent/90 shadow-lg hover:shadow-xl transition-all duration-300"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Analyzing Firmware...
                    </>
                  ) : (
                    <>
                      <Shield className="mr-2 h-5 w-5" />
                      Analyze Firmware
                    </>
                  )}
                </Button>
              </div>
            </>
          ) : (
            <>
              {/* Results Section */}
              <div className="mb-6 flex justify-between items-center">
                <h2 className="text-2xl font-bold text-primary">Analysis Results</h2>
                <Button
                  onClick={() => {
                    setResults(null);
                    setOldCode([]);
                    setNewCode([]);
                    setOldDocs([]);
                    setNewDocs([]);
                    setOldBinary([]);
                    setNewBinary([]);
                    setCurrentStep(0);
                    setIsAnalyzing(false);
                  }}
                  variant="outline"
                  className="hover:bg-secondary hover:text-secondary-foreground"
                >
                  New Analysis
                </Button>
              </div>
              <AnalysisResults results={results} />
            </>
          )}

          {/* Floating Debug Button */}
          <div className="fixed bottom-6 right-6 z-50">
            <Button
              onClick={() => setShowDebugPanel(!showDebugPanel)}
              className="h-12 w-12 rounded-full shadow-lg bg-amber-600 hover:bg-amber-700 text-white"
              title="Toggle Debug Panel"
            >
              <Bug className="h-5 w-5" />
            </Button>
          </div>

          {/* Debug Panel Modal/Popup */}
          {showDebugPanel && (
            <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/50">
              <div className="relative w-[90%] max-w-4xl h-[80%] max-h-[600px] m-4">
                <DebugPanel className="h-full" />
                <Button
                  onClick={() => setShowDebugPanel(false)}
                  className="absolute top-4 right-4 z-10 bg-red-500 hover:bg-red-600 text-white border-red-500 hover:border-red-600"
                  size="sm"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;