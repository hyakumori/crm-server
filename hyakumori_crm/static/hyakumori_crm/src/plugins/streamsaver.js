import streamSaver from "streamsaver";

streamSaver.mitm = process.env.NODE_ENV === "/mitm.html";

export default streamSaver;
