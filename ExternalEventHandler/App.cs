using Autodesk.Revit.UI;

namespace RevitExternalEventHandler
{
    public class App : IExternalApplication
    {
        private static ExternalEvent _externalEvent;
        private static ExternalEventHandler _handler;

        public Result OnStartup(UIControlledApplication application)
        {
            _handler = new ExternalEventHandler();
            _externalEvent = ExternalEvent.Create(_handler);

            RevitWebService webService = new RevitWebService(_externalEvent, _handler);
            webService.Start();

            return Result.Succeeded;
        }

        public Result OnShutdown(UIControlledApplication application)
        {
            return Result.Succeeded;
        }
    }
}
