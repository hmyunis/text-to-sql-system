import { useState } from 'react';
import { useSqlQuery } from './hooks/useSqlQuery';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './components/ui/table';
import { Database, Play, Loader2, Info, X } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL;

export default function App() {
  const [question, setQuestion] = useState('');
  const [isEvalOpen, setIsEvalOpen] = useState(false);
  const [isEvalLoading, setIsEvalLoading] = useState(false);
  const [evalError, setEvalError] = useState('');
  const [evalResult, setEvalResult] = useState<any>(null);
  const { askMutation, schemaQuery } = useSqlQuery();

  type ParsedTable = {
    raw: string;
    table: string | null;
    columns: string[];
  };

  const parsedSchema = (schemaQuery.data || '')
    .split(/CREATE TABLE/i)
    .filter(Boolean)
    .map((chunk: any) => `CREATE TABLE${chunk}`)
    .map((statement: string) => {
      const match = statement.match(/CREATE TABLE\s+([^\s(]+)\s*\(([^)]*)\)/i);
      if (!match) {
        return { raw: statement.trim(), table: null, columns: [] as string[] };
      }
      const [, table, columnsRaw] = match;
      const columns = columnsRaw
        .split(',')
        .map((col: string) => col.trim())
        .filter(Boolean);
      return { raw: statement.trim(), table, columns };
    }) as ParsedTable[];

  const handleRun = () => {
    if (!question) return toast.error("Please enter a question");
    askMutation.mutate(question, {
      onError: (err: any) => toast.error(err.response?.data?.error || "Failed to fetch"),
      onSuccess: (data) => {
        if (data.error) toast.warning(data.error);
        else toast.success("Query executed successfully");
      }
    });
  };

  const handleOpenEvaluation = async () => {
    setIsEvalOpen(true);
    setIsEvalLoading(true);
    setEvalError('');
    setEvalResult(null);

    try {
      const { data } = await axios.get(`${API_BASE}/evaluate/`);
      setEvalResult(data);
    } catch (err: any) {
      setEvalError(err.response?.data?.error || 'Failed to run evaluation');
    } finally {
      setIsEvalLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-full bg-slate-50 text-slate-900 overflow-hidden">
      <aside className="w-96 border-r bg-linear-to-b from-white to-slate-50 p-6 overflow-y-auto">
        <div className="flex items-center gap-3 mb-6">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-600/10">
            <Database className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h2 className="font-bold text-lg">Database Schema</h2>
            <p className="text-xs text-slate-500">Tables and columns</p>
          </div>
        </div>
        {schemaQuery.isLoading ? (
          <div className="space-y-2">
            {[1, 2, 3].map((i: number) => (
              <div key={i} className="h-4 bg-slate-100 animate-pulse rounded" />
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {parsedSchema.map((table: ParsedTable, i: number) => (
              <div key={i} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                {table.table ? (
                  <>
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-semibold text-slate-800">{table.table}</h3>
                      <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600">
                        {table.columns.length} cols
                      </span>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {table.columns.map((col: string) => (
                        <span
                          key={col}
                          className="rounded-lg border border-slate-200 bg-slate-50 px-2 py-1 text-xs font-mono text-slate-600"
                        >
                          {col}
                        </span>
                      ))}
                    </div>
                  </>
                ) : (
                  <p className="text-xs font-mono text-slate-500">{table.raw}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </aside>

      <main className="flex-1 p-8 overflow-y-auto">
        <div className="max-w-5xl mx-auto space-y-6">
          <header>
            <h1 className="text-3xl font-bold tracking-tight">Text-to-SQL Interface</h1>
            <p className="text-slate-500 mt-2">Ask questions about your data in plain English.</p>
            <div className="mt-4">
              <Button variant="outline" onClick={handleOpenEvaluation} className="gap-2">
                <Database className="h-4 w-4" />
                Run Evaluation
              </Button>
            </div>
          </header>

          <div className="flex gap-3">
            <Input 
              placeholder='e.g., "List all customers who live in Adama"' 
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="text-lg h-14"
              onKeyDown={(e) => e.key === 'Enter' && handleRun()}
            />
            <Button size="lg" className="px-8 h-14" onClick={handleRun} disabled={askMutation.isPending}>
              {askMutation.isPending ? <Loader2 className="animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
              Run
            </Button>
          </div>

          {askMutation.data && !askMutation.data.error && (
            <Card className="border-blue-100 bg-white shadow-sm">
              <CardHeader className="bg-slate-50 border-b py-3">
                <CardTitle className="text-sm font-mono text-blue-700 flex items-center gap-2">
                  <Info className="w-4 h-4" /> Generated SQL: {askMutation.data.sql}
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <div className="max-h-125 overflow-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        {askMutation.data.columns.map((col: string) => (
                          <TableHead key={col} className="bg-slate-50 uppercase text-[11px] font-bold">{col}</TableHead>
                        ))}
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {askMutation.data.data.map((row: any, idx: number) => (
                        <TableRow key={idx}>
                          {askMutation.data.columns.map((col: string) => (
                            <TableCell key={col}>{row[col]}</TableCell>
                          ))}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          )}

          {askMutation.isPending && (
            <div className="space-y-4">
              <div className="h-10 bg-slate-200 animate-pulse rounded w-1/2" />
              <div className="h-40 bg-slate-100 animate-pulse rounded" />
            </div>
          )}
        </div>
      </main>

      {isEvalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm"
            onClick={() => setIsEvalOpen(false)}
          />
          <div className="relative w-full max-w-3xl rounded-2xl border border-slate-200 bg-white p-6 shadow-xl">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold">Execution Accuracy Evaluation</h2>
                <p className="text-sm text-slate-500">Runs the gold standard test set and checks execution match.</p>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setIsEvalOpen(false)}>
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="mt-6">
              {isEvalLoading && (
                <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4">
                  <Loader2 className="h-5 w-5 animate-spin text-slate-600" />
                  <span className="text-sm font-medium text-slate-700">Running evaluation...</span>
                </div>
              )}

              {!isEvalLoading && evalError && (
                <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                  {evalError}
                </div>
              )}

              {!isEvalLoading && evalResult && (
                <div className="space-y-6">
                  <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6 text-center">
                    <p className="text-xs uppercase tracking-widest text-slate-500">Overall Accuracy</p>
                    <div className="mt-2 text-5xl font-bold text-slate-900">
                      {evalResult.overall_accuracy_percent}
                    </div>
                    <p className="mt-2 text-sm text-slate-500">{evalResult.metric}</p>
                  </div>

                  <div className="rounded-xl border border-slate-200 overflow-hidden">
                    <div className="bg-slate-50 px-4 py-2 text-xs font-semibold uppercase text-slate-600">
                      Detailed Results
                    </div>
                    <div className="max-h-80 overflow-auto divide-y">
                      {evalResult.detailed_results?.map((row: any, idx: number) => (
                        <div key={idx} className="p-4">
                          <div className="flex items-center justify-between">
                            <p className="font-medium text-slate-800">{row.question}</p>
                            <span
                              className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                                row.status === 'PASS'
                                  ? 'bg-emerald-100 text-emerald-700'
                                  : 'bg-red-100 text-red-700'
                              }`}
                            >
                              {row.status}
                            </span>
                          </div>
                          <div className="mt-2 grid gap-2 text-xs text-slate-600">
                            <div className="font-mono">Generated: {row.generated_sql}</div>
                            <div className="font-mono">Expected: {row.expected_sql}</div>
                            {row.debug && <div>Debug: {row.debug}</div>}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
