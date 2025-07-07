"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { Button } from "@/components/ui/Button";
import { Textarea } from "@/components/ui/Textarea";

const sampleQueries = [
  "ویژگی‌های هر یک از ۵ اپیزود سیکل بازار مسکن (رکود شدید، رکود اندک، رونق اندک، رونق شدید، چرخش بازار) چیست؟",
  "بر اساس کدام شاخص‌ها (حجم معاملات، روند قیمت، تعداد جواز ساخت) می‌توان فاز فعلی بازار مسکن را تشخیص داد؟",
  "چهار گروه اصلی خریدار مسکن (سرمایه‌گذار، سوداگر، مصرفی رفاه‌گرا، مصرفی مقتصد) چه رفتاری در اپیزودهای مختلف بازار از خود نشان می‌دهند؟",
  "افزایش یا کاهش درآمدهای نفتی دولت چگونه بر تشدید رونق یا تعمیق رکود در بازار مسکن تأثیر می‌گذارد؟",
  "سیاست‌های پولی انبساطی یا انقباضی (تغییر در رشد نقدینگی و تسهیلات) چه تأثیر مستقیمی بر سیکل‌های بازار مسکن دارد؟",
  "عوامل کلیدی شکل‌گیری حباب قیمتی در بازار مسکن ایران چیست و نقش نقدینگی در این فرآیند چگونه است؟",
  "چه راهکارهای سیاست‌گذاری برای مدیریت حباب‌های دارایی و کنترل فعالیت‌های سوداگرانه وجود دارد؟",
  "ارزیابی طرح مسکن مهر از منظر تأثیر بر اقتصاد کلان، بازار و نظام بانکی چگونه است و چه درس‌هایی برای پروژه‌های آتی دارد؟",
  "روند تحولات جمعیتی کشور (مانند تعداد ازدواج) چگونه تقاضای واقعی و بلندمدت مسکن را تحت تأثیر قرار خواهد داد؟",
  "چرا استراتژی «خرید و نگهداری بلندمدت» در بازار مسکن ایران بهینه نیست و چه سیاستی می‌تواند به افزایش نقدشوندگی بازار کمک کند؟",
];

export default function Home() {
  const [query, setQuery] = useState("");
  const [report, setReport] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showSampleQuestions, setShowSampleQuestions] = useState(false);

  const handleGenerateReport = async () => {
    if (!query) return;
    setIsLoading(true);
    setReport("");

    try {
      const response = await fetch("http://localhost:8000/generate_report_stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query, language: "Persian" }),
      });

      if (!response.body) {
        throw new Error("Response body is null");
      }

      const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          break;
        }

        const lines = value.split("\n\n").filter(line => line.length > 0);
        for (const line of lines) {
          if (line.startsWith("data:")) {
            const jsonString = line.substring(6);
            try {
              const data = JSON.parse(jsonString);
              if (data.type === "chunk") {
                setReport((prev) => prev + data.content);
              }
            } catch (e) {
              console.error("Error parsing JSON from stream", e);
            }
          }
        }
      }
    } catch (error) {
      console.error(error);
      setReport("خطا در تولید گزارش. لطفاً دوباره تلاش کنید.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-4 sm:p-10 bg-gray-50 font-sans" dir="rtl">
      <div className="w-full max-w-4xl">
        <header className="text-center mb-10">
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-gray-800">تحلیل  فرانیک</h1>
          <p className="text-sm sm:text-base text-gray-600 mt-2">
            هوشمندترین دستیار شما در تحلیل بازار املاک و مستغلات
          </p>
        </header>

        <div className="bg-white p-4 sm:p-6 rounded-lg shadow-lg">
          <Textarea
            className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-shadow"
            rows={4}
            placeholder="پرس و جوی خود را در اینجا وارد کنید... (مثلاً 'تحلیل بازار مسکن در تهران')"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <Button
            className="mt-4 w-full bg-blue-600 text-white p-3 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 disabled:bg-blue-400 disabled:cursor-not-allowed transition-all duration-300 ease-in-out"
            onClick={handleGenerateReport}
            disabled={isLoading || !query}
          >
            {isLoading ? (
              <div className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                در حال تولید گزارش...
              </div>
            ) : "تولید گزارش"}
          </Button>
        </div>

        {isLoading && (
          <div className="mt-8 bg-white p-6 rounded-lg shadow-lg animate-pulse">
             <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
             <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
             <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
             <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          </div>
        )}

        {report && !isLoading && (
          <div className="prose prose-lg max-w-none mt-8 bg-white p-4 sm:p-8 rounded-lg shadow-lg" dir="rtl">
            <ReactMarkdown
              components={{
                p: (props) => <p dir="auto" {...props} />,
                h1: (props) => <h1 dir="auto" {...props} />,
                h2: (props) => <h2 dir="auto" {...props} />,
                h3: (props) => <h3 dir="auto" {...props} />,
                h4: (props) => <h4 dir="auto" {...props} />,
                h5: (props) => <h5 dir="auto" {...props} />,
                h6: (props) => <h6 dir="auto" {...props} />,
                li: (props) => <li dir="auto" {...props} />,
                th: (props) => <th dir="auto" {...props} />,
                td: (props) => <td dir="auto" {...props} />,
              }}
            >
              {report}
            </ReactMarkdown>
          </div>
        )}
        
        {!isLoading && (
          <div className="text-center mt-6">
            <Button
              variant="ghost"
              className="text-blue-600 hover:text-blue-800"
              onClick={() => setShowSampleQuestions(!showSampleQuestions)}
            >
              {showSampleQuestions ? "مخفی کردن سوالات نمونه" : "نمایش سوالات نمونه"}
            </Button>
          </div>
        )}

        {showSampleQuestions && !isLoading && (
          <div className="mt-8 sm:mt-10">
            <h2 className="text-lg sm:text-xl font-semibold mb-4 text-gray-700 text-center">
              یا از سوالات نمونه انتخاب کنید
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {sampleQueries.map((q, index) => (
                <div
                  key={index}
                  className="bg-white p-3 sm:p-4 rounded-lg shadow-lg cursor-pointer hover:bg-gray-100 hover:shadow-xl transition-all duration-300"
                  onClick={() => {
                    setQuery(q);
                    setShowSampleQuestions(false);
                  }}
                >
                  <p className="text-xs sm:text-sm text-gray-800">{q}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
