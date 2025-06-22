"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [task, setTask] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  useEffect(() => {
    const interval = setInterval(async () => {
      if (!task) {
        return;
      }
      const { status } = await fetch(`/api/status/${task}`).then((r) =>
        r.json()
      );
      setMessage(`status: ${status}`);
      if (status === "done") {
        setDone(true);
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [task]);

  const handleUpload = async () => {
    if (!file) {
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    const { tid } = await fetch("/api/verbatim", {
      body: formData,
      method: "POST",
    }).then((r) => r.json());

    setTask(tid);
    setMessage(`task ${tid} is ready to go!`);
  };

  const dl = async () => {
    fetch(`/api/dl/${task}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("File not found or failed to fetch");
        }
        return response.blob();
      })
      .then((blob) => {
        const link = document.createElement("a");
        const url = window.URL.createObjectURL(blob);
        const name = file!.name.replace(/\.[^/.]+$/, "");
        link.href = url;
        link.download = `${name}.tex`;
        link.click();
        window.URL.revokeObjectURL(url);
      });
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
        <div className="flex justify-between">
          <Button onClick={handleUpload} disabled={!file}>
            Upload
          </Button>
          <Button onClick={dl} disabled={!done}>
            Download
          </Button>
        </div>
        {message && <p className="mt-4 text-sm text-gray-700">{message}</p>}
      </div>
    </main>
  );
}
