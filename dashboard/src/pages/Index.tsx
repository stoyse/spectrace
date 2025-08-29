import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Shield, Upload, FileCode, CheckCircle, ArrowRight, Lock } from 'lucide-react';

const Index = () => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b border-border">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <img 
                src="/android-chrome-512x512.png" 
                alt="SpecTrace Logo" 
                className="h-8 w-8 rounded-lg"
              />
              <span className="text-xl font-bold text-primary">SpecTrace</span>
            </div>
            <Button 
              variant="outline"
              onClick={() => window.location.href = '/dashboard'}
            >
              Get Started
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-24 px-4 relative overflow-hidden bg-gradient-to-br from-background via-secondary/5 to-accent/10">
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-primary/20 via-transparent to-transparent"></div>
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-accent/20 via-transparent to-transparent"></div>
        </div>
        <div className="container mx-auto text-center max-w-5xl relative z-10">
          <div className="mb-12">
            <div className="inline-flex items-center px-4 py-2 bg-secondary/10 border border-secondary/20 rounded-full mb-8 backdrop-blur-sm">
              <Shield className="h-4 w-4 text-secondary mr-2" />
              <span className="text-sm font-medium text-secondary">Advanced Firmware Security Platform</span>
            </div>
            <h1 className="text-6xl md:text-7xl font-bold bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent mb-8 leading-tight tracking-tight">
              SpecTrace
            </h1>
            <h2 className="text-3xl md:text-4xl text-foreground font-bold mb-8 tracking-wide">
              AI-Powered Firmware Analysis
            </h2>
            <p className="text-xl text-muted-foreground mb-12 max-w-3xl mx-auto leading-relaxed">
              <span className="text-secondary font-semibold">Upload. Compare. Secure.</span>
              <br />
              Get instant insights into firmware changes, detect anomalies, and mitigate security risks with cutting-edge AI technology.
            </p>
          </div>
          
          <div className="mb-16">
            <Button 
              size="lg" 
              className="bg-gradient-to-r from-secondary via-secondary/90 to-accent hover:from-secondary/80 hover:to-accent/80 text-white px-12 py-4 text-lg font-semibold shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105 border-0 rounded-xl"
              onMouseEnter={() => setIsHovered(true)}
              onMouseLeave={() => setIsHovered(false)}
              onClick={() => window.location.href = '/dashboard'}
            >
              <Shield className={`mr-3 h-6 w-6 transition-all duration-300 ${isHovered ? 'scale-110 rotate-12' : ''}`} />
              Start Secure Analysis
            </Button>
          </div>
        </div>
      </section>

      {/* Description Section */}
      <section className="py-20 px-4 bg-gradient-to-b from-muted/20 to-background border-y border-border/50">
        <div className="container mx-auto max-w-5xl">
          <div className="text-center mb-16">
            <h3 className="text-2xl font-bold text-primary mb-6">Revolutionizing Firmware Security</h3>
            <p className="text-lg text-foreground leading-relaxed max-w-4xl mx-auto">
              SpecTrace leverages advanced AI algorithms to analyze and compare firmware code with unprecedented accuracy. 
              Simply upload your files and let our intelligent system detect differences, flag potential 
              security vulnerabilities, and provide actionable insights. Designed for security professionals, 
              developers, and researchers, SpecTrace makes firmware analysis <span className="text-secondary font-semibold">simple, reliable, and scalable</span>.
            </p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 px-4 bg-gradient-to-b from-background to-muted/10">
        <div className="container mx-auto max-w-7xl">
          <div className="text-center mb-20">
            <div className="inline-flex items-center px-4 py-2 bg-primary/10 border border-primary/20 rounded-full mb-8 backdrop-blur-sm">
              <FileCode className="h-4 w-4 text-primary mr-2" />
              <span className="text-sm font-medium text-primary">Secure Analysis Workflow</span>
            </div>
            <h3 className="text-4xl md:text-5xl font-bold text-primary mb-6 tracking-tight">How It Works</h3>
            <p className="text-muted-foreground text-xl max-w-2xl mx-auto">Three powerful steps to comprehensive firmware security analysis</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
            <Card className="text-center border-0 bg-gradient-to-br from-secondary/5 to-secondary/10 backdrop-blur-sm hover:from-secondary/10 hover:to-secondary/15 transition-all duration-500 hover:shadow-xl hover:-translate-y-2 group relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-transparent via-transparent to-secondary/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <CardHeader className="relative z-10 pb-6">
                <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-secondary via-secondary/90 to-secondary/70 rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:rotate-3 transition-all duration-500 shadow-lg">
                  <Upload className="h-10 w-10 text-white" />
                </div>
                <CardTitle className="text-2xl text-secondary font-bold mb-4">1. Upload Files</CardTitle>
              </CardHeader>
              <CardContent className="relative z-10">
                <p className="text-muted-foreground text-base leading-relaxed">
                  Securely upload your original and updated firmware code along with specification files for comprehensive analysis.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center border-0 bg-gradient-to-br from-accent/5 to-accent/10 backdrop-blur-sm hover:from-accent/10 hover:to-accent/15 transition-all duration-500 hover:shadow-xl hover:-translate-y-2 group relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-transparent via-transparent to-accent/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <CardHeader className="relative z-10 pb-6">
                <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-accent via-accent/90 to-accent/70 rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:rotate-3 transition-all duration-500 shadow-lg">
                  <FileCode className="h-10 w-10 text-white" />
                </div>
                <CardTitle className="text-2xl text-accent font-bold mb-4">2. AI Analysis</CardTitle>
              </CardHeader>
              <CardContent className="relative z-10">
                <p className="text-muted-foreground text-base leading-relaxed">
                  Advanced AI algorithms compare code changes, analyze specifications, and validate security compliance automatically.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center border-0 bg-gradient-to-br from-green-500/5 to-green-600/10 backdrop-blur-sm hover:from-green-500/10 hover:to-green-600/15 transition-all duration-500 hover:shadow-xl hover:-translate-y-2 group relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-transparent via-transparent to-green-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <CardHeader className="relative z-10 pb-6">
                <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-green-500 via-green-500/90 to-green-600 rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:rotate-3 transition-all duration-500 shadow-lg">
                  <CheckCircle className="h-10 w-10 text-white" />
                </div>
                <CardTitle className="text-2xl text-green-600 font-bold mb-4">3. Get Results</CardTitle>
              </CardHeader>
              <CardContent className="relative z-10">
                <p className="text-muted-foreground text-base leading-relaxed">
                  Receive detailed security insights, comprehensive risk assessments, and actionable recommendations for enhanced firmware security.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-4 bg-gradient-to-br from-primary/90 via-secondary to-accent/90 text-white relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-white/10 via-transparent to-transparent"></div>
          <div className="absolute inset-0 bg-black/30"></div>
        </div>
        <div className="container mx-auto text-center max-w-4xl relative z-10">
          <div className="inline-flex items-center px-4 py-2 bg-white/10 border border-white/20 rounded-full mb-8 backdrop-blur-sm">
            <Lock className="h-4 w-4 text-white mr-2" />
            <span className="text-sm font-medium text-white">Enterprise-Grade Security</span>
          </div>
          <h3 className="text-4xl md:text-5xl font-bold mb-8 tracking-tight">Ready to Secure Your Firmware?</h3>
          <p className="text-xl md:text-2xl mb-12 opacity-90 leading-relaxed max-w-3xl mx-auto">
            Join security professionals and developers worldwide using SpecTrace for 
            <span className="font-semibold"> comprehensive firmware analysis and threat detection</span>.
          </p>
          <Button 
            size="lg" 
            className="bg-white text-primary hover:bg-white/95 px-12 py-4 text-lg font-semibold shadow-2xl hover:shadow-3xl transition-all duration-300 transform hover:scale-105 rounded-xl border-0"
            onClick={() => window.location.href = '/dashboard'}
          >
            Get Started Now
            <ArrowRight className="ml-3 h-6 w-6" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-border">
        <div className="container mx-auto text-center">
          <div className="flex items-center justify-center mb-4">
            <img 
              src="/android-chrome-512x512.png" 
              alt="SpecTrace Logo" 
              className="h-6 w-6 rounded-md mr-2"
            />
            <span className="font-semibold text-primary">SpecTrace</span>
          </div>
          <p className="text-sm text-muted-foreground mb-2">
            AI-Powered Firmware Analysis Platform
          </p>
          <p className="text-xs text-muted-foreground/80">
            AI Cybersecurity Hackathon - Sponsored by SAP & KPMG
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
