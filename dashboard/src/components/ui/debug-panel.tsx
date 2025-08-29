import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { debugStore, StoredResponse } from '@/lib/debug-store';
import { Bug, ChevronDown, ChevronRight, Trash2, RefreshCw } from 'lucide-react';

interface DebugPanelProps {
  className?: string;
}

export const DebugPanel: React.FC<DebugPanelProps> = ({ className = '' }) => {
  const [responses, setResponses] = useState<StoredResponse[]>([]);
  const [expandedItems, setExpandedItems] = useState<Set<number>>(new Set());

  const refreshResponses = () => {
    setResponses(debugStore.getAllResponses());
  };

  useEffect(() => {
    refreshResponses();
    // Refresh every 2 seconds to show new responses
    const interval = setInterval(refreshResponses, 2000);
    return () => clearInterval(interval);
  }, []);

  const toggleExpanded = (index: number) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedItems(newExpanded);
  };

  const clearAll = () => {
    debugStore.clearAll();
    setResponses([]);
    setExpandedItems(new Set());
  };

  const getStatusColor = (status: number) => {
    if (status >= 200 && status < 300) return 'bg-green-500';
    if (status >= 400 && status < 500) return 'bg-yellow-500';
    if (status >= 500) return 'bg-red-500';
    return 'bg-gray-500';
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const formatEndpoint = (url: string) => {
    try {
      return new URL(url).pathname;
    } catch {
      return url;
    }
  };

  return (
    <Card className={`${className} border-amber-200 bg-white shadow-lg`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between mb-2">
          <CardTitle className="flex items-center gap-2 text-amber-700">
            <Bug className="h-5 w-5" />
            Debug Panel - API Responses
          </CardTitle>
        </div>
        <div className="flex items-center justify-between">
          <p className="text-sm text-amber-600">
            {responses.length} stored response{responses.length !== 1 ? 's' : ''}
          </p>
          <div className="flex gap-2">
            <Button size="sm" variant="outline" onClick={refreshResponses} title="Refresh">
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button size="sm" variant="outline" onClick={clearAll} title="Clear All">
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <ScrollArea className="h-96">
          {responses.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No API responses captured yet. Make an analysis to see debug data.
            </div>
          ) : (
            <div className="space-y-2">
              {responses.map((response, index) => (
                <Collapsible
                  key={index}
                  open={expandedItems.has(index)}
                  onOpenChange={() => toggleExpanded(index)}
                >
                  <CollapsibleTrigger asChild>
                    <div className="flex items-center gap-2 p-2 hover:bg-amber-100/50 rounded cursor-pointer border border-amber-200">
                      {expandedItems.has(index) ? (
                        <ChevronDown className="h-4 w-4" />
                      ) : (
                        <ChevronRight className="h-4 w-4" />
                      )}
                      <Badge
                        className={`${getStatusColor(response.responseStatus)} text-white text-xs px-2 py-1`}
                      >
                        {response.responseStatus || 'ERR'}
                      </Badge>
                      <span className="font-mono text-sm text-blue-700">
                        {response.method}
                      </span>
                      <span className="flex-1 text-sm truncate">
                        {formatEndpoint(response.endpoint)}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {formatDuration(response.duration)}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {new Date(response.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                  </CollapsibleTrigger>
                  <CollapsibleContent>
                    <div className="ml-6 mt-2 space-y-3 p-3 bg-white rounded border border-amber-200">
                      <div>
                        <h4 className="text-sm font-semibold mb-1">Request Body:</h4>
                        <pre className="text-xs bg-gray-50 p-2 rounded overflow-auto max-h-32">
                          {JSON.stringify(response.requestBody, null, 2)}
                        </pre>
                      </div>
                      <Separator />
                      <div>
                        <h4 className="text-sm font-semibold mb-1">Response Data:</h4>
                        <pre className="text-xs bg-gray-50 p-2 rounded overflow-auto max-h-48">
                          {response.error 
                            ? `Error: ${response.error}`
                            : JSON.stringify(response.responseData, null, 2)
                          }
                        </pre>
                      </div>
                      <Separator />
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>Status: {response.responseStatus}</span>
                        <span>Duration: {formatDuration(response.duration)}</span>
                        <span>Time: {new Date(response.timestamp).toLocaleString()}</span>
                      </div>
                    </div>
                  </CollapsibleContent>
                </Collapsible>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
};