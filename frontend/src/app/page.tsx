"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    // const res = await fetch("/api/upload", {
    //   method: "POST",
    //   body: formData,
    // });

    // const data = await res.json();
    setMessage("ok it's uploaded");
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-6 bg-gray-100">
      <div className="bg-white p-8 rounded shadow-md w-full max-w-md">
        <h1 className="text-xl font-bold mb-4">Upload PDF</h1>
        <Label htmlFor="pdf">Select a PDF file</Label>
        <Input
          id="pdf"
          type="file"
          accept="application/pdf"
          onChange={(e) => {
            const selected = e.target.files?.[0];
            if (selected?.type === "application/pdf") {
              setFile(selected);
              setMessage(null);
            } else {
              setMessage("Please select a valid PDF file.");
              setFile(null);
            }
          }}
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
