import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { AlertTriangle, CheckCircle, Shield, FileText, Code, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AnalysisResultsProps {
  results: {
    code_analysis: any;
    doc_analysis: any;
    compliance_status: string;
    compliance_score: number;
    mismatches: any[];
    matches: any[];
    summary: any;
    recommendations: string[];
  };
}

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({ results }) => {
  const getRiskColor = (risk: string) => {
    switch (risk?.toLowerCase()) {
      case 'low': return 'text-green-600 bg-green-100 border-green-200';
      case 'medium': return 'text-amber-600 bg-amber-100 border-amber-200';
      case 'high': return 'text-destructive bg-destructive/10 border-destructive/20';
      default: return 'text-muted-foreground bg-muted border-border';
    }
  };

  const getComplianceColor = (score: number) => {
    if (score >= 0.9) return 'text-green-600 bg-green-100 border-green-200';
    if (score >= 0.7) return 'text-amber-600 bg-amber-100 border-amber-200';
    return 'text-destructive bg-destructive/10 border-destructive/20';
  };

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Risk Assessment</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{results.code_analysis?.risk_assessment || 'N/A'}</div>
            <Badge className={cn('text-xs', getRiskColor(results.code_analysis?.risk_assessment))}>
              {results.code_analysis?.security_findings?.length || 0} findings
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compliance Score</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{Math.round(results.compliance_score * 100)}%</div>
            <Badge className={cn('text-xs', getComplianceColor(results.compliance_score))}>
              {results.compliance_status}
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Changes</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{results.summary?.total_code_changes || 0}</div>
            <p className="text-xs text-muted-foreground">
              Code & Specifications
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Code Analysis */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Code className="h-5 w-5" />
            Code Analysis
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {results.code_analysis?.differences?.length > 0 ? (
            <div className="space-y-3">
              <h4 className="text-sm font-medium">Key Changes:</h4>
              {results.code_analysis.differences.slice(0, 5).map((diff: any, index: number) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-muted rounded-lg">
                  <Badge variant={diff.change_type === 'added' ? 'default' : diff.change_type === 'removed' ? 'destructive' : 'secondary'}>
                    {diff.change_type}
                  </Badge>
                  <div className="flex-1">
                    <p className="text-sm">{diff.context}</p>
                    {diff.line_number && (
                      <p className="text-xs text-muted-foreground">Line {diff.line_number}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">No code changes detected.</p>
          )}
        </CardContent>
      </Card>

      {/* Specification Analysis */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Specification Analysis
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {results.doc_analysis?.differences?.length > 0 ? (
            <div className="space-y-3">
              <h4 className="text-sm font-medium">Specification Changes:</h4>
              {results.doc_analysis.differences.map((diff: any, index: number) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-muted rounded-lg">
                  <Badge variant={diff.change_type === 'added' ? 'default' : diff.change_type === 'removed' ? 'destructive' : 'secondary'}>
                    {diff.change_type}
                  </Badge>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{diff.section}</p>
                    <p className="text-sm text-muted-foreground">{diff.description}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">No specification changes detected.</p>
          )}
        </CardContent>
      </Card>

      {/* Compliance Matches */}
      {results.matches?.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              Compliance Matches
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {results.matches.map((match: any, index: number) => (
                <div key={index} className="p-3 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-sm font-medium text-green-800 mb-1">{match.description}</p>
                  <div className="text-xs text-green-700 space-y-1">
                    <p><span className="font-medium">Code:</span> {match.code_reference}</p>
                    <p><span className="font-medium">Specification:</span> {match.doc_reference}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Compliance Mismatches */}
      {results.mismatches?.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              Compliance Mismatches
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {results.mismatches.map((mismatch: any, index: number) => (
                <div key={index} className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm font-medium text-red-800 mb-1">{mismatch.description}</p>
                  <div className="text-xs text-red-700 space-y-1">
                    <p><span className="font-medium">Code:</span> {mismatch.code_reference}</p>
                    <p><span className="font-medium">Specification:</span> {mismatch.doc_reference}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Summary */}
      {results.summary && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Analysis Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div className="space-y-2">
                <p className="text-sm"><span className="font-medium">Total Code Changes:</span> {results.summary.total_code_changes}</p>
                <p className="text-sm"><span className="font-medium">Total Doc Changes:</span> {results.summary.total_doc_changes}</p>
              </div>
              <div className="space-y-2">
                <p className="text-sm"><span className="font-medium">Matched Changes:</span> {results.summary.matched_changes}</p>
                <p className="text-sm"><span className="font-medium">Unmatched Changes:</span> {results.summary.unmatched_changes}</p>
              </div>
            </div>
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">{results.summary.overall_assessment}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recommendations */}
      {results.recommendations?.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {results.recommendations.map((rec: string, index: number) => (
                <div key={index} className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-secondary mt-0.5 flex-shrink-0" />
                  <p className="text-sm">{rec}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};