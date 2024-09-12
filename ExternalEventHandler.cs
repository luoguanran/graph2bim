using System;
using System.CodeDom.Compiler;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using IronPython.Hosting;
using Newtonsoft.Json;

namespace RevitExternalEventHandler
{
    public class ExternalEventHandler : IExternalEventHandler
    {
        public string CodeToExecute { get; set; }
        public string ExecutionResult { get; private set; } // 保存执行结果

        public void Execute(UIApplication app)
        {
            Log("ExternalEventHandler executed.");
            TaskDialog.Show("Info", "ExternalEventHandler executed.");

            // 在这里解析并执行生成的代码
            ExecutionResult = ExecuteRevitCode(app, CodeToExecute);
        }

        // 添加一个方法用于重置ExecutionResult
        public void ResetExecutionResult()
        {
            ExecutionResult = null;
        }

        public string GetName()
        {
            return "ExternalEventHandler";
        }

        private string ExecuteRevitCode(UIApplication app, string code)
        {
            Log("ExecuteRevitCode called with code: " + code);
            TaskDialog.Show("Info", "ExecuteRevitCode called with code: " + code);

            var engine = Python.CreateEngine();
            var scope = engine.CreateScope();

            // 将doc和app传递给Python脚本
            scope.SetVariable("doc", app.ActiveUIDocument.Document);
            scope.SetVariable("uidoc", app.ActiveUIDocument);
            scope.SetVariable("app", app);

            try
            {
                engine.Execute(code, scope);

                // 获取Python脚本中的result变量
                dynamic result = scope.GetVariable("result");

                // 将结果转换为JSON字符串返回
                string jsonResult = JsonConvert.SerializeObject(result);
                Log("result: " + jsonResult);
                return jsonResult;
            }
            catch (Exception ex)
            {
                TaskDialog.Show("Error", "Exception: " + ex.Message);
                Log("Exception: " + ex.Message);
                return JsonConvert.SerializeObject(new { error = ex.Message });
            }
        }

        private void Log(string message)
        {
            string path = @"D:\PHD\BIM+AI\ExternalEventHandler_log.txt";
            using (StreamWriter sw = File.AppendText(path))
            {
                sw.WriteLine(DateTime.Now.ToString() + ": " + message);
            }
        }
    }
}
