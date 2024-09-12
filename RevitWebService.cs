using System;
using System.Net;
using System.Threading.Tasks;
using Autodesk.Revit.UI;
using System.IO;
using Newtonsoft.Json;

namespace RevitExternalEventHandler
{
    public class RevitWebService
    {
        private readonly ExternalEvent _externalEvent;
        private readonly ExternalEventHandler _handler;

        public RevitWebService(ExternalEvent externalEvent, ExternalEventHandler handler)
        {
            _externalEvent = externalEvent;
            _handler = handler;
        }

        public void Start()
        {
            HttpListener listener = new HttpListener();
            listener.Prefixes.Add("http://localhost:5000/execute_revit_code/");
            listener.Start();
            Log("Web service started, listening on http://localhost:5000/execute_revit_code/");

            Task.Run(() =>
            {
                while (true)
                {
                    var context = listener.GetContext();
                    var request = context.Request;
                    var response = context.Response;

                    if (request.HttpMethod == "POST")
                    {
                        using (var reader = new StreamReader(request.InputStream, request.ContentEncoding))
                        {
                            string code = reader.ReadToEnd();
                            Log("Received code: " + code);
                            _handler.CodeToExecute = code;
                            _externalEvent.Raise();

                            // 等待ExternalEventHandler执行完毕
                            while (_handler.ExecutionResult == null)
                            {
                                System.Threading.Thread.Sleep(100);
                            }

                            // 将结果返回给客户端
                            string responseString = _handler.ExecutionResult;
                            byte[] buffer = System.Text.Encoding.UTF8.GetBytes(responseString);
                            response.ContentLength64 = buffer.Length;
                            var output = response.OutputStream;
                            output.Write(buffer, 0, buffer.Length);
                            output.Close();

                            // 重置ExecutionResult以处理下一次请求
                            _handler.ResetExecutionResult();
                        }
                    }
                }
            });
        }

        private void Log(string message)
        {
            string path = @"D:\PHD\BIM+AI\revit_web_service_log.txt";
            using (StreamWriter sw = File.AppendText(path))
            {
                sw.WriteLine(DateTime.Now.ToString() + ": " + message);
            }
        }
    }

}
