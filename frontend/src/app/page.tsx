"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { SSE } from "@/lib/sse";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const handleUpload = async () => {
    if (!file) {
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    // @ts-ignore bro
    const eventSource = new SSE("/api/process", {
      payload: formData,
      method: "POST",
    });
    eventSource.addEventListener("message", console.log);
    eventSource.addEventListener("end", (e: any) => {
      console.log(e);
      eventSource.close();
    });

    setMessage("sent!");
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (!selected) return;

    const allowedTypes = [
      "application/pdf",
      "image/png",
      "image/jpeg",
      "image/jpg",
    ];

    if (allowedTypes.includes(selected.type)) {
      setFile(selected);
      setMessage(null);
    } else {
      setFile(null);
      setMessage("Only PDF or image files (JPG, PNG) are allowed.");
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-6 bg-gray-100">
      <div className="bg-white p-8 rounded shadow-md w-full max-w-md">
        <h1 className="text-xl font-bold mb-4">Upload PDF or Image</h1>
        <Label htmlFor="upload">Select a PDF or Image</Label>
        <Input
          id="upload"
          type="file"
          accept=".pdf,image/png,image/jpeg"
          onChange={handleFileChange}
          className="mb-4"
        />
        <Button onClick={handleUpload} disabled={!file}>
          Upload
        </Button>
        {message && <p className="mt-4 text-sm text-gray-700">{message}</p>}
      </div>
    </main>
  );
}
