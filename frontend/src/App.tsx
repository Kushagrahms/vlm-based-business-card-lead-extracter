import {type ChangeEvent,useState,useEffect,type DragEvent,useMemo} from "react";
import "./App.css";

type Lead= {
  id?:number;
  first_name:string;
  last_name:string;
  job_title:string;
  company:string;
  location:string;
  phone_number:string;
  email:string;
  source_filename?:string;
};

type ExtractResponse={
  count:number;
  leads:{
    filename:string;
    data:Lead;
  }[];
};

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function App(){
  const [files,setFiles] = useState<File[]>([]);
  const [leads,setLeads] = useState<Lead[]>([]);
  const [processing,setProcessing] = useState(false);
  const [loadingLeads,setLoadingLeads] = useState(true);
  const [error,setError] = useState("");
  const [dragging,setDragging] = useState(false);

  const imageFiles = useMemo(
    ()=> files.filter((file)=>file.type.startsWith("image/")),
    [files]
  );

    // --------------------------------------------------
  // LOAD EXISTING LEADS
  // --------------------------------------------------

  const fetchLeads = async()=>{
    try{
    setLoadingLeads(true);
    const response = await fetch(`${API_BASE}/api/leads`);
    if(!response.ok){
      throw new Error("could not load saved leads");
    }
    const data = await response.json();
    
    setLeads(data.leads || []);
  }catch(err){
    console.error(err);
  }finally{
    setLoadingLeads(false);
  }
 };

 useEffect(()=>{
  fetchLeads();
 },[]);

  // ADD FILES
 const add_files = (incomingFiles : File[])=>{
  setError("");

  const validFiles = incomingFiles.filter((file)=>
  file.type.startsWith("image/"));

  if (validFiles.length !== incomingFiles.length){
    setError("Only image files are supported");
  }
  setFiles ((currentFiles)=>{
    const existing = new Set(
      currentFiles.map(
        (file)=>`${file.name}-${file.size}-${file.lastModified}`
       )
      );
      const newFiles = validFiles.filter(
        (file)=>!existing.has(`${file.name}-${file.size}-${file.lastModified}`)
      );

      return [...currentFiles,...newFiles];
   });
 };
  // FILE INPUT

 const handleFileInput = (
  event: ChangeEvent<HTMLInputElement> 
 ) =>{
  add_files(Array.from(event.target.files || []));

  event.target.value = "";
 };

  // DRAG & DROP

 const handleDrop = (
  event: DragEvent<HTMLDivElement>
 )=>{
  event.preventDefault();
  setDragging(false);
  add_files(Array.from(event.dataTransfer.files));
 };

  // REMOVE FILE
 const removeFile = (index:number)=>{
  setFiles((currentFiles)=>
  currentFiles.filter((_,i)=>i!==index));
 };
// EXTRACT LEADS
 const extractLeads = async()=>{
  if(imageFiles.length == 0){
    setError("please Upload a business card");
    return
  }

  setProcessing(true);
  setError("");

  try{
    const formData = new FormData();
    imageFiles.forEach((file)=>{
      formData.append("files",file);
    });
    const response = await fetch(
      `${API_BASE}/api/leads/extract`,
      {
        method:"POST",
        body:formData,
      }
    );
    const data = await response.json();
    if(!response.ok){
      throw new Error( data.detail || "Lead extraction failed.");
    }
    const result = data as ExtractResponse;

    const extractedLeads = result.leads.map(
      (item)=>({
        ...item.data, source_filename:item.filename,
      })
    );
    setLeads((current)=>[
      ...extractedLeads,...current,
    ]);
    setFiles([]);
  }
  catch(err){
    setError( err instanceof Error ?err.message : "Something went wrong");
  }
  finally{
    setProcessing(false);
  }
 };
 // EXCEL EXPORT
 const downloadExcel = async()=>{
  try{
    setError("");
    const response = await fetch(`${API_BASE}/api/leads/export`);

    if(!response.ok){
      throw new Error("Excel file failed");
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "Business_Card_leads.xlsx";

    document.body.appendChild(link);

    link.click();
    link.remove();

    URL.revokeObjectURL(url);
  }
  catch(err){
    setError(
      err instanceof Error ?err.message:"Export file failed"
    );
  }
 };
  // DISPLAY NAME
 const getName = (lead:Lead)=>{
  const name = [
    lead.first_name,
    lead.last_name,
  ]
  .filter(Boolean).join(" ");
  return name || "-"
 };

 return (
    <div className="app">

      {/* HEADER */}

      <header className="header">

        <div className="brand">

          <div className="brand-icon">
            L
          </div>

          <div>
            <div className="brand-name">
              LeadLens
            </div>

            <div className="brand-subtitle">
              VLM business card intelligence
            </div>
          </div>

        </div>

        <div className="api-status">
          <span />
          API connected
        </div>

      </header>


      {/* MAIN */}

      <main className="container">

        {/* HERO */}

        <section className="hero">

          <div>

            <div className="eyebrow">
              AI-POWERED LEAD CAPTURE
            </div>

            <h1>
              Turn business cards into
              <span> structured leads.</span>
            </h1>

            <p>
              Upload multiple business cards at once.
              Vision-language AI extracts the contact
              information and turns it into clean,
              structured lead data.
            </p>

          </div>

          <div className="lead-counter">

            <strong>
              {leads.length}
            </strong>

            <span>
              saved leads
            </span>

          </div>

        </section>


        {/* WORKSPACE */}

        <section className="workspace">

          {/* UPLOAD CARD */}

          <div className="panel">

            <div className="panel-header">

              <div>

                <div className="section-label">
                  01 / UPLOAD
                </div>

                <h2>
                  Business cards
                </h2>

              </div>

              {files.length > 0 && (
                <button
                  className="clear-button"
                  onClick={() => setFiles([])}
                >
                  Clear all
                </button>
              )}

            </div>


            {/* DROPZONE */}

            <div
              className={`dropzone ${
                dragging ? "dragging" : ""
              }`}
              onDragEnter={(event) => {
                event.preventDefault();
                setDragging(true);
              }}
              onDragOver={(event) =>
                event.preventDefault()
              }
              onDragLeave={() =>
                setDragging(false)
              }
              onDrop={handleDrop}
            >

              <input
                id="file-upload"
                type="file"
                accept="image/*"
                multiple
                onChange={handleFileInput}
              />

              <label
                htmlFor="file-upload"
                className="dropzone-content"
              >

                <div className="upload-icon">

                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                  >
                    <path
                      d="M12 16V4"
                      stroke="currentColor"
                      strokeWidth="1.5"
                    />

                    <path
                      d="M7.5 8.5L12 4L16.5 8.5"
                      stroke="currentColor"
                      strokeWidth="1.5"
                    />

                    <path
                      d="M5 15V18.5C5 19.3284 5.67157 20 6.5 20H17.5C18.3284 20 19 19.3284 19 18.5V15"
                      stroke="currentColor"
                      strokeWidth="1.5"
                    />

                  </svg>

                </div>

                <h3>
                  Drop your business cards here
                </h3>

                <p>
                  or <span>browse files</span> from
                  your computer
                </p>

                <small>
                  PNG, JPG, JPEG, WEBP · Multiple
                  files supported
                </small>

              </label>

            </div>


            {/* FILE PREVIEWS */}

            {files.length > 0 && (

              <div className="preview-grid">

                {files.map((file, index) => (

                  <div
                    className="preview"
                    key={`${file.name}-${index}`}
                  >

                    <img
                      src={URL.createObjectURL(file)}
                      alt=""
                    />

                    <div className="preview-info">

                      <strong>
                        {file.name}
                      </strong>

                      <span>
                        {(
                          file.size /
                          1024 /
                          1024
                        ).toFixed(2)}{" "}
                        MB
                      </span>

                    </div>

                    <button
                      className="remove-file"
                      onClick={() =>
                        removeFile(index)
                      }
                    >
                      ×
                    </button>

                  </div>

                ))}

              </div>

            )}


            {/* UPLOAD FOOTER */}

            <div className="upload-footer">

              <span>
                {imageFiles.length} image
                {imageFiles.length !== 1
                  ? "s"
                  : ""}{" "}
                selected
              </span>

              <button
                className="primary-button"
                onClick={extractLeads}
                disabled={
                  processing ||
                  imageFiles.length === 0
                }
              >

                {processing ? (
                  <>
                    <span className="spinner" />
                    Extracting...
                  </>
                ) : (
                  <>
                    Extract leads
                    <span>→</span>
                  </>
                )}

              </button>

            </div>

          </div>


          {/* HOW IT WORKS */}

          <aside className="info-panel">

            <div className="section-label">
              HOW IT WORKS
            </div>

            <div className="step">

              <b>01</b>

              <div>
                <strong>
                  Upload
                </strong>

                <p>
                  Select one or many business
                  card images.
                </p>
              </div>

            </div>

            <div className="step">

              <b>02</b>

              <div>
                <strong>
                  Extract
                </strong>

                <p>
                  Vision-language AI reads
                  the card information.
                </p>
              </div>

            </div>

            <div className="step">

              <b>03</b>

              <div>
                <strong>
                  Export
                </strong>

                <p>
                  Review leads and download
                  them as Excel.
                </p>
              </div>

            </div>

          </aside>

        </section>


        {/* ERROR */}

        {error && (

          <div className="error">

            <div className="error-symbol">
              !
            </div>

            <span>
              {error}
            </span>

            <button
              onClick={() => setError("")}
            >
              ×
            </button>

          </div>

        )}


        {/* RESULTS */}

        <section className="results">

          <div className="results-header">

            <div>

              <div className="section-label">
                02 / RESULTS
              </div>

              <div className="results-title">

                <h2>
                  Extracted leads
                </h2>

                <span>
                  {leads.length}
                </span>

              </div>

            </div>


            <button
              className="export-button"
              onClick={downloadExcel}
              disabled={leads.length === 0}
            >

              <svg
                viewBox="0 0 24 24"
                fill="none"
              >

                <path
                  d="M12 4V15"
                  stroke="currentColor"
                  strokeWidth="1.5"
                />

                <path
                  d="M8 11L12 15L16 11"
                  stroke="currentColor"
                  strokeWidth="1.5"
                />

                <path
                  d="M5 19H19"
                  stroke="currentColor"
                  strokeWidth="1.5"
                />

              </svg>

              Export Excel

            </button>

          </div>


          {/* TABLE */}

          <div className="table-container">

            {loadingLeads ? (

              <div className="empty-state">

                <span className="spinner dark" />

                <p>
                  Loading saved leads...
                </p>

              </div>

            ) : leads.length === 0 ? (

              <div className="empty-state">

                <div className="empty-icon">
                  ◎
                </div>

                <h3>
                  No leads yet
                </h3>

                <p>
                  Upload business cards above
                  and extract their information.
                </p>

              </div>

            ) : (

              <table>

                <thead>

                  <tr>
                    <th>Name</th>
                    <th>Job title</th>
                    <th>Company</th>
                    <th>Location</th>
                    <th>Phone</th>
                    <th>Email</th>
                    <th>Source</th>
                  </tr>

                </thead>

                <tbody>

                  {leads.map(
                    (lead, index) => (

                      <tr
                        key={
                          lead.id ??
                          `${lead.source_filename}-${index}`
                        }
                      >

                        <td>
                          <strong>
                            {getName(lead)}
                          </strong>
                        </td>

                        <td>
                          {lead.job_title || "—"}
                        </td>

                        <td>
                          {lead.company || "—"}
                        </td>

                        <td>
                          {lead.location || "—"}
                        </td>

                        <td>
                          {lead.phone_number ||
                            "—"}
                        </td>

                        <td>
                          {lead.email || "—"}
                        </td>

                        <td>

                          <span className="source">
                            {lead.source_filename ||
                              "—"}
                          </span>

                        </td>

                      </tr>

                    )
                  )}

                </tbody>

              </table>

            )}

          </div>

        </section>


        {/* FOOTER */}

        <footer>

          <span>
            LeadLens
          </span>

          <span>
            Business Card Lead Extraction System
          </span>

          <span>
            Qwen Vision-Language Model
          </span>

        </footer>

      </main>

    </div>
  );
}

export default App;